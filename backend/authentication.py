from django.http import JsonResponse
from functools import wraps
from utils import decode_jwt
from db import users_collection
from bson import ObjectId

def login_required(view_func):
    """Decorator to require login via JWT."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized, token missing'}, status=401)
        
        token = auth_header.split(' ')[1]
        payload = decode_jwt(token)
        if not payload:
            return JsonResponse({'error': 'Unauthorized, token invalid or expired'}, status=401)
        
        user_id = payload.get('user_id')
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return JsonResponse({'error': 'User not found'}, status=401)
        
        request.user_id = str(user['_id'])
        request.user_role = user.get('role', 'customer')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
