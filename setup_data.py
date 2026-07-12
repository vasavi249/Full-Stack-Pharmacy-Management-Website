import os
import django

import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import datetime
import shutil
from db import users_collection, categories_collection, medicines_collection
from utils import hash_password

def setup_images():
    images = {
        'pain_relief': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\pain_relief_meds_1783833969906.png',
        'diabetes': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\diabetes_meds_1783833980506.png',
        'vitamins': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\vitamin_supplements_1783833991792.png',
        'skincare': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\skincare_cream_1783834001439.png',
        'babycare': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\baby_care_products_1783834012988.png',
        
        'paracetamol_650': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\paracetamol_650_1783834197755.png',
        'dolo_650': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\dolo_650_1783834208574.png',
        'metformin_500': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\metformin_500_1783834221190.png',
        'vitamin_c': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\vitamin_c_1783834236871.png',
        'moisturizing_cream': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\moisturizing_cream_1783834347843.png',
        'baby_powder': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\baby_powder_1783834364071.png',
        'insulin_glargine': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\insulin_glargine_1783834375364.png',
        'vitamin_d3': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\vitamin_d3_1783834385256.png',
        'ibuprofen_400': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\ibuprofen_400_1783834399082.png',
        'sunscreen_spf50': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\sunscreen_spf50_1783834408732.png',
        'baby_diapers': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\baby_diapers_1783834425622.png',
        'glimepiride_2mg': r'C:\Users\gorla\.gemini\antigravity-ide\brain\11513bee-1359-4f31-baac-6a5f1e0773e3\glimepiride_2mg_1783834436067.png'
    }
    dest_dir = os.path.join(BASE_DIR, 'frontend', 'images')
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for name, src in images.items():
        if os.path.exists(src):
            shutil.copy(src, os.path.join(dest_dir, f'{name}.png'))

def generate_sample_data():
    setup_images()
    print("Clearing old data...")
    users_collection.delete_many({})
    categories_collection.delete_many({})
    medicines_collection.delete_many({})
    
    print("Inserting Users...")
    users = [
        {
            "name": "Admin",
            "email": "admin@pharmacy.com",
            "password": hash_password("admin123"),
            "role": "admin",
            "phone": "9999999999",
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "name": "Rahul Sharma",
            "email": "rahul@gmail.com",
            "password": hash_password("rahul123"),
            "role": "customer",
            "phone": "9876543210",
            "address": "123 Main St, New Delhi",
            "createdAt": datetime.datetime.utcnow()
        },
        {
            "name": "Priya Verma",
            "email": "priya@gmail.com",
            "password": hash_password("priya123"),
            "role": "customer",
            "phone": "8765432109",
            "address": "456 High St, Mumbai",
            "createdAt": datetime.datetime.utcnow()
        }
    ]
    users_collection.insert_many(users)

    print("Inserting Categories...")
    categories = [
        {"categoryName": "Pain Relief", "description": "Medicines for pain and fever"},
        {"categoryName": "Diabetes", "description": "Diabetes management medications"},
        {"categoryName": "Vitamin Supplements", "description": "Health and vitamin supplements"},
        {"categoryName": "Skin Care", "description": "Dermatological products"},
        {"categoryName": "Baby Care", "description": "Products for infants and babies"}
    ]
    categories_collection.insert_many(categories)

    print("Inserting Medicines...")
    medicines = [
        {
            "medicineName": "Paracetamol 650",
            "brand": "GSK",
            "category": "Pain Relief",
            "price": 30.0,
            "stock": 100,
            "description": "Used for pain relief and fever.",
            "image": "images/paracetamol_650.png",
            "expiryDate": "2025-12-31",
            "manufacturer": "GSK"
        },
        {
            "medicineName": "Dolo 650",
            "brand": "Micro Labs",
            "category": "Pain Relief",
            "price": 32.0,
            "stock": 150,
            "description": "Effective for mild to moderate pain and fever.",
            "image": "images/dolo_650.png",
            "expiryDate": "2025-10-31",
            "manufacturer": "Micro Labs"
        },
        {
            "medicineName": "Metformin 500",
            "brand": "Sun Pharma",
            "category": "Diabetes",
            "price": 18.0,
            "stock": 50,
            "description": "Controls high blood sugar in type 2 diabetes.",
            "image": "images/metformin_500.png",
            "expiryDate": "2026-05-20",
            "manufacturer": "Sun Pharma"
        },
        {
            "medicineName": "Vitamin C Tablets",
            "brand": "Cipla",
            "category": "Vitamin Supplements",
            "price": 23.0,
            "stock": 200,
            "description": "Immunity booster vitamin C supplements.",
            "image": "images/vitamin_c.png",
            "expiryDate": "2025-08-15",
            "manufacturer": "Cipla"
        },
        {
            "medicineName": "Moisturizing Cream",
            "brand": "Cetaphil",
            "category": "Skin Care",
            "price": 450.0,
            "stock": 30,
            "description": "Daily moisturizing cream for dry sensitive skin.",
            "image": "images/moisturizing_cream.png",
            "expiryDate": "2026-01-10",
            "manufacturer": "Galderma"
        },
        {
            "medicineName": "Baby Powder",
            "brand": "Johnson's",
            "category": "Baby Care",
            "price": 105.0,
            "stock": 80,
            "description": "Mild and gentle baby powder for everyday use.",
            "image": "images/baby_powder.png",
            "expiryDate": "2027-02-15",
            "manufacturer": "Johnson & Johnson"
        },
        {
            "medicineName": "Insulin Glargine",
            "brand": "Lantus",
            "category": "Diabetes",
            "price": 750.0,
            "stock": 25,
            "description": "Long-acting insulin used to treat diabetes mellitus.",
            "image": "images/insulin_glargine.png",
            "expiryDate": "2025-11-20",
            "manufacturer": "Sanofi"
        },
        {
            "medicineName": "Vitamin D3 60K",
            "brand": "Lumia",
            "category": "Vitamin Supplements",
            "price": 110.0,
            "stock": 150,
            "description": "Cholecalciferol chewable tablets for bone health.",
            "image": "images/vitamin_d3.png",
            "expiryDate": "2026-09-10",
            "manufacturer": "Sun Pharma"
        },
        {
            "medicineName": "Ibuprofen 400",
            "brand": "Brufen",
            "category": "Pain Relief",
            "price": 20.0,
            "stock": 120,
            "description": "Nonsteroidal anti-inflammatory drug (NSAID) for pain.",
            "image": "images/ibuprofen_400.png",
            "expiryDate": "2025-06-30",
            "manufacturer": "Abbott"
        },
        {
            "medicineName": "Sunscreen SPF 50",
            "brand": "Neutrogena",
            "category": "Skin Care",
            "price": 675.0,
            "stock": 60,
            "description": "Broad spectrum UVA/UVB protection sunscreen.",
            "image": "images/sunscreen_spf50.png",
            "expiryDate": "2026-04-12",
            "manufacturer": "Johnson & Johnson"
        },
        {
            "medicineName": "Baby Diapers",
            "brand": "Pampers",
            "category": "Baby Care",
            "price": 449.0,
            "stock": 200,
            "description": "Ultra-soft and absorbent diapers for newborn babies.",
            "image": "images/baby_diapers.png",
            "expiryDate": "2028-01-01",
            "manufacturer": "Procter & Gamble"
        },
        {
            "medicineName": "Glimepiride 2mg",
            "brand": "Amaryl",
            "category": "Diabetes",
            "price": 130.0,
            "stock": 70,
            "description": "Oral blood-sugar-lowering drug for type 2 diabetes.",
            "image": "images/glimepiride_2mg.png",
            "expiryDate": "2026-11-20",
            "manufacturer": "Sanofi"
        },
        {
            "medicineName": "B-Complex Forte",
            "brand": "Becosules",
            "category": "Vitamin Supplements",
            "price": 46.0,
            "stock": 300,
            "description": "B-complex vitamins with Vitamin C capsule.",
            "image": "images/vitamins.png",
            "expiryDate": "2025-07-25",
            "manufacturer": "Pfizer"
        },
        {
            "medicineName": "Acne Gel",
            "brand": "Benzac",
            "category": "Skin Care",
            "price": 180.0,
            "stock": 45,
            "description": "Topical gel treatment for mild to moderate acne.",
            "image": "images/skincare.png",
            "expiryDate": "2025-10-15",
            "manufacturer": "Galderma"
        },
        {
            "medicineName": "Baby Massage Oil",
            "brand": "Himalaya",
            "category": "Baby Care",
            "price": 110.0,
            "stock": 85,
            "description": "Daily massage oil for baby's healthy growth.",
            "image": "images/babycare.png",
            "expiryDate": "2026-05-18",
            "manufacturer": "Himalaya Wellness"
        }
    ]
    medicines_collection.insert_many(medicines)

    print("Sample data successfully populated!")

if __name__ == "__main__":
    generate_sample_data()
