import json
import datetime
from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from db import users_collection, categories_collection, medicines_collection, cart_collection, orders_collection
from utils import hash_password, verify_password, generate_jwt, json_encoder
from authentication import login_required
from permissions import admin_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        return json_encoder(obj)

def send_response(data, status=200):
    return JsonResponse(data, status=status, encoder=MongoEncoder, safe=False)

# --- AUTHENTICATION APIs ---

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    data = request.json
    email = data.get('email')
    if users_collection.find_one({'email': email}):
        return send_response({'error': 'Email already exists'}, 400)
    
    user = {
        'name': data.get('name'),
        'email': email,
        'phone': data.get('phone', ''),
        'password': hash_password(data.get('password')),
        'address': data.get('address', ''),
        'role': data.get('role', 'customer'),
        'createdAt': datetime.datetime.utcnow()
    }
    result = users_collection.insert_one(user)
    return send_response({'message': 'Registered successfully', 'userId': result.inserted_id}, 201)

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = users_collection.find_one({'email': email})
    
    if not user or not verify_password(password, user['password']):
        return send_response({'error': 'Invalid credentials'}, 401)
    
    token = generate_jwt(user['_id'], user['role'])
    return send_response({
        'token': token,
        'user': {
            'id': user['_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    return send_response({'message': 'Logged out successfully'})

@csrf_exempt
@require_http_methods(["GET", "PUT"])
@login_required
def profile(request):
    if request.method == "GET":
        user = users_collection.find_one({'_id': ObjectId(request.user_id)}, {'password': 0})
        return send_response(user)
    elif request.method == "PUT":
        data = request.json
        update_data = {
            'name': data.get('name'),
            'phone': data.get('phone'),
            'address': data.get('address')
        }
        if data.get('password'):
            update_data['password'] = hash_password(data['password'])
            
        users_collection.update_one(
            {'_id': ObjectId(request.user_id)},
            {'$set': {k: v for k, v in update_data.items() if v is not None}}
        )
        return send_response({'message': 'Profile updated'})

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def profile_password(request):
    data = request.json
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    
    user = users_collection.find_one({'_id': ObjectId(request.user_id)})
    if not user or not verify_password(old_password, user['password']):
        return send_response({'error': 'Incorrect old password'}, 400)
        
    users_collection.update_one(
        {'_id': ObjectId(request.user_id)},
        {'$set': {'password': hash_password(new_password)}}
    )
    return send_response({'message': 'Password updated successfully'})

# --- CATEGORY APIs ---

@csrf_exempt
def category_list(request):
    if request.method == "GET":
        categories = list(categories_collection.find())
        return send_response(categories)
    elif request.method == "POST":
        return category_create(request)

@login_required
@admin_required
def category_create(request):
    data = request.json
    cat = {
        'categoryName': data.get('categoryName'),
        'description': data.get('description', '')
    }
    result = categories_collection.insert_one(cat)
    cat['_id'] = result.inserted_id
    return send_response(cat, 201)

@csrf_exempt
def category_detail(request, pk):
    if request.method == "GET":
        cat = categories_collection.find_one({'_id': ObjectId(pk)})
        return send_response(cat) if cat else send_response({'error': 'Not found'}, 404)
    elif request.method == "PUT":
        return category_update(request, pk)
    elif request.method == "DELETE":
        return category_delete(request, pk)

@login_required
@admin_required
def category_update(request, pk):
    data = request.json
    categories_collection.update_one({'_id': ObjectId(pk)}, {'$set': data})
    return send_response({'message': 'Updated'})

@login_required
@admin_required
def category_delete(request, pk):
    categories_collection.delete_one({'_id': ObjectId(pk)})
    return send_response({'message': 'Deleted'})

# --- MEDICINE APIs ---

@csrf_exempt
def medicine_list(request):
    if request.method == "GET":
        medicines = list(medicines_collection.find())
        return send_response(medicines)
    elif request.method == "POST":
        return medicine_create(request)

@login_required
@admin_required
def medicine_create(request):
    data = request.POST.dict() if request.POST else request.json
    image_url = ""
    if request.FILES.get('image'):
        file = request.FILES['image']
        path = default_storage.save(f'medicines/{file.name}', ContentFile(file.read()))
        image_url = f'/media/{path}'
    elif data.get('image'):
        image_url = data.get('image')

    med = {
        'medicineName': data.get('medicineName'),
        'brand': data.get('brand'),
        'category': data.get('category'),
        'price': float(data.get('price', 0)),
        'stock': int(data.get('stock', 0)),
        'description': data.get('description', ''),
        'image': image_url,
        'expiryDate': data.get('expiryDate'),
        'manufacturer': data.get('manufacturer')
    }
    result = medicines_collection.insert_one(med)
    med['_id'] = result.inserted_id
    return send_response(med, 201)

@csrf_exempt
def medicine_detail(request, pk):
    if request.method == "GET":
        med = medicines_collection.find_one({'_id': ObjectId(pk)})
        return send_response(med) if med else send_response({'error': 'Not found'}, 404)
    elif request.method == "PUT":
        return medicine_update(request, pk)
    elif request.method == "DELETE":
        return medicine_delete(request, pk)

@login_required
@admin_required
def medicine_update(request, pk):
    data = request.POST.dict() if request.POST else request.json
    update_data = {k: v for k, v in data.items() if k not in ['_id']}
    if 'price' in update_data: update_data['price'] = float(update_data['price'])
    if 'stock' in update_data: update_data['stock'] = int(update_data['stock'])
    
    if request.FILES.get('image'):
        file = request.FILES['image']
        path = default_storage.save(f'medicines/{file.name}', ContentFile(file.read()))
        update_data['image'] = f'/media/{path}'

    medicines_collection.update_one({'_id': ObjectId(pk)}, {'$set': update_data})
    return send_response({'message': 'Updated'})

@login_required
@admin_required
def medicine_delete(request, pk):
    medicines_collection.delete_one({'_id': ObjectId(pk)})
    return send_response({'message': 'Deleted'})

@csrf_exempt
@require_http_methods(["GET"])
def medicine_search(request):
    q = request.GET.get('q', '')
    regex = {'$regex': q, '$options': 'i'}
    results = list(medicines_collection.find({
        '$or': [{'medicineName': regex}, {'brand': regex}, {'category': regex}]
    }))
    return send_response(results)

@csrf_exempt
@require_http_methods(["GET"])
def medicine_by_category(request, category):
    results = list(medicines_collection.find({'category': category}))
    return send_response(results)

@csrf_exempt
@require_http_methods(["GET"])
def medicine_low_stock(request):
    results = list(medicines_collection.find({'stock': {'$lt': 20}}))
    return send_response(results)


# --- CART APIs ---

@csrf_exempt
@login_required
def cart_view(request):
    if request.method == "GET":
        cart = cart_collection.find_one({'userId': request.user_id})
        if not cart:
            cart = {'userId': request.user_id, 'items': [], 'total': 0}
            cart_collection.insert_one(cart)
        
        # Populate medicine details
        for item in cart['items']:
            med = medicines_collection.find_one({'_id': ObjectId(item['medicineId'])})
            item['medicine'] = med
        return send_response(cart)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cart_add(request):
    data = request.json
    medicine_id = data.get('medicineId')
    qty = int(data.get('quantity', 1))
    
    med = medicines_collection.find_one({'_id': ObjectId(medicine_id)})
    if not med or med.get('stock', 0) < qty:
        return send_response({'error': 'Insufficient stock'}, 400)
    
    price = med.get('price', 0)
    
    cart = cart_collection.find_one({'userId': request.user_id})
    if not cart:
        cart = {'userId': request.user_id, 'items': [], 'total': 0}
        cart_collection.insert_one(cart)
        
    items = cart.get('items', [])
    found = False
    for item in items:
        if item['medicineId'] == medicine_id:
            item['quantity'] += qty
            found = True
            break
    if not found:
        items.append({'medicineId': medicine_id, 'quantity': qty, 'price': price})
        
    total = sum(i['price'] * i['quantity'] for i in items)
    cart_collection.update_one({'userId': request.user_id}, {'$set': {'items': items, 'total': total}})
    return send_response({'message': 'Added to cart'})

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def cart_update(request):
    data = request.json
    medicine_id = data.get('medicineId')
    qty = int(data.get('quantity', 1))
    
    cart = cart_collection.find_one({'userId': request.user_id})
    if cart:
        items = cart.get('items', [])
        for item in items:
            if item['medicineId'] == medicine_id:
                item['quantity'] = qty
                break
        total = sum(i['price'] * i['quantity'] for i in items)
        cart_collection.update_one({'userId': request.user_id}, {'$set': {'items': items, 'total': total}})
    return send_response({'message': 'Cart updated'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def cart_remove(request, pk):
    cart = cart_collection.find_one({'userId': request.user_id})
    if cart:
        items = [i for i in cart.get('items', []) if i['medicineId'] != pk]
        total = sum(i['price'] * i['quantity'] for i in items)
        cart_collection.update_one({'userId': request.user_id}, {'$set': {'items': items, 'total': total}})
    return send_response({'message': 'Item removed'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def cart_clear(request):
    cart_collection.update_one({'userId': request.user_id}, {'$set': {'items': [], 'total': 0}})
    return send_response({'message': 'Cart cleared'})


# --- ORDER APIs ---

@csrf_exempt
@login_required
def order_list(request):
    if request.method == "GET":
        if request.user_role == 'admin':
            orders = list(orders_collection.find().sort('createdAt', -1))
        else:
            orders = list(orders_collection.find({'userId': request.user_id}).sort('createdAt', -1))
            
        for order in orders:
            for item in order.get('items', []):
                item['medicine'] = medicines_collection.find_one({'_id': ObjectId(item['medicineId'])})
            order['user'] = users_collection.find_one({'_id': ObjectId(order['userId'])}, {'password': 0})
        return send_response(orders)
    elif request.method == "POST":
        return order_create(request)

@login_required
def order_create(request):
    data = request.json
    cart = cart_collection.find_one({'userId': request.user_id})
    if not cart or not cart.get('items'):
        return send_response({'error': 'Cart is empty'}, 400)
    
    # Check stock
    for item in cart['items']:
        med = medicines_collection.find_one({'_id': ObjectId(item['medicineId'])})
        if not med or med.get('stock', 0) < item['quantity']:
            return send_response({'error': f'Insufficient stock for {med.get("medicineName")}'}, 400)
            
    order = {
        'userId': request.user_id,
        'items': cart['items'],
        'totalAmount': cart['total'],
        'paymentMethod': data.get('paymentMethod', 'Cash on Delivery'),
        'status': 'Pending',
        'createdAt': datetime.datetime.utcnow()
    }
    result = orders_collection.insert_one(order)
    
    # Reduce stock
    for item in cart['items']:
        medicines_collection.update_one(
            {'_id': ObjectId(item['medicineId'])},
            {'$inc': {'stock': -item['quantity']}}
        )
        
    # Clear cart
    cart_collection.update_one({'userId': request.user_id}, {'$set': {'items': [], 'total': 0}})
    
    return send_response({'message': 'Order placed', 'orderId': result.inserted_id}, 201)

@csrf_exempt
@login_required
def order_detail(request, pk):
    if request.method == "GET":
        order = orders_collection.find_one({'_id': ObjectId(pk)})
        if not order:
            return send_response({'error': 'Not found'}, 404)
        if request.user_role != 'admin' and order['userId'] != request.user_id:
            return send_response({'error': 'Unauthorized'}, 403)
            
        for item in order.get('items', []):
            item['medicine'] = medicines_collection.find_one({'_id': ObjectId(item['medicineId'])})
        order['user'] = users_collection.find_one({'_id': ObjectId(order['userId'])}, {'password': 0})
        return send_response(order)
    elif request.method == "PUT":
        return order_update(request, pk)
    elif request.method == "DELETE":
        return order_delete(request, pk)

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def order_cancel(request, pk):
    order = orders_collection.find_one({'_id': ObjectId(pk)})
    if not order:
        return send_response({'error': 'Order not found'}, 404)
        
    if order['userId'] != request.user_id:
        return send_response({'error': 'Unauthorized'}, 403)
        
    if order['status'] != 'Pending':
        return send_response({'error': 'Only pending orders can be cancelled'}, 400)
        
    # Revert stock
    for item in order.get('items', []):
        medicines_collection.update_one(
            {'_id': ObjectId(item['medicineId'])},
            {'$inc': {'stock': item['quantity']}}
        )
        
    orders_collection.update_one({'_id': ObjectId(pk)}, {'$set': {'status': 'Cancelled'}})
    return send_response({'message': 'Order cancelled successfully'})

@login_required
@admin_required
def order_update(request, pk):
    data = request.json
    status = data.get('status')
    if status:
        orders_collection.update_one({'_id': ObjectId(pk)}, {'$set': {'status': status}})
    return send_response({'message': 'Order updated'})

@login_required
@admin_required
def order_delete(request, pk):
    orders_collection.delete_one({'_id': ObjectId(pk)})
    return send_response({'message': 'Order deleted'})

# --- DASHBOARD APIs ---

@csrf_exempt
@require_http_methods(["GET"])
@login_required
@admin_required
def dashboard_stats(request):
    total_medicines = medicines_collection.count_documents({})
    total_categories = categories_collection.count_documents({})
    total_users = users_collection.count_documents({'role': 'customer'})
    total_orders = orders_collection.count_documents({})
    
    revenue_pipeline = [
        {"$match": {"status": {"$in": ["Delivered", "Packed", "Dispatched", "Confirmed"]}}},
        {"$group": {"_id": None, "totalRevenue": {"$sum": "$totalAmount"}}}
    ]
    revenue_agg = list(orders_collection.aggregate(revenue_pipeline))
    revenue = revenue_agg[0]['totalRevenue'] if revenue_agg else 0
    
    low_stock_medicines = list(medicines_collection.find({'stock': {'$lt': 20}}))
    recent_orders = list(orders_collection.find().sort('createdAt', -1).limit(5))
    for order in recent_orders:
        order['user'] = users_collection.find_one({'_id': ObjectId(order['userId'])}, {'password': 0})
    
    return send_response({
        'totalMedicines': total_medicines,
        'totalCategories': total_categories,
        'totalUsers': total_users,
        'totalOrders': total_orders,
        'revenue': revenue,
        'lowStockMedicines': low_stock_medicines,
        'recentOrders': recent_orders
    })

@csrf_exempt
@require_http_methods(["GET"])
@login_required
@admin_required
def dashboard_revenue(request):
    # Daily revenue for chart
    pipeline = [
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$createdAt"}},
            "revenue": {"$sum": "$totalAmount"}
        }},
        {"$sort": {"_id": 1}}
    ]
    data = list(orders_collection.aggregate(pipeline))
    return send_response(data)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
@admin_required
def dashboard_users(request):
    # Get all users for admin
    users = list(users_collection.find({'role': 'customer'}, {'password': 0}))
    return send_response(users)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
@admin_required
def user_delete(request, pk):
    users_collection.delete_one({'_id': ObjectId(pk)})
    return send_response({'message': 'User deleted'})

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
@admin_required
def user_toggle_status(request, pk):
    user = users_collection.find_one({'_id': ObjectId(pk)})
    if not user:
        return send_response({'error': 'User not found'}, 404)
        
    new_status = 'blocked' if user.get('status') != 'blocked' else 'active'
    users_collection.update_one({'_id': ObjectId(pk)}, {'$set': {'status': new_status}})
    return send_response({'message': f'User {new_status} successfully'})
