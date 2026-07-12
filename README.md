# Pharmacy Management Website

A complete Full Stack Pharmacy Management Web Application built with HTML/CSS/Vanilla JS (Frontend) and Django + PyMongo (Backend).

## Features
- **Authentication**: JWT based authentication (Register, Login, Role-Based Access).
- **Customer Features**: Browse Medicines, Search/Filter, Cart, Checkout, Order History, Profile Update.
- **Admin Features**: Admin Dashboard (Charts/Stats), Manage Medicines (CRUD, Images), Manage Categories, Manage Users, Update Order Status.
- **Responsive Design**: Mobile First, Glassmorphism, CSS Grid, Flexbox, Animations.

## Folder Structure
```
PharmacyManagement/
│
├── backend/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── db.py (MongoDB raw connection)
│   ├── utils.py (JWT, Bcrypt)
│   └── ...
│
├── frontend/
│   ├── css/index.css
│   ├── js/script.js
│   ├── index.html
│   ├── admin-dashboard.html
│   └── ...
│
├── media/ (For image uploads)
├── static/
├── screenshots/
├── requirements.txt
├── setup_data.py
└── README.md
```

## Installation & Setup

### 1. MongoDB Setup
Ensure you have a local MongoDB instance running on `mongodb://localhost:27017/`. The database `pharmacy_db` and its collections will be created automatically.

### 2. Backend Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Generate Sample Data
Run the custom python script to populate users, categories, and medicines:
```bash
python setup_data.py
```

### 4. Run Server
Start the Django development server:
```bash
cd backend
python manage.py runserver
```

### 5. Run Frontend
Since it's pure HTML/JS using Fetch API, you can serve the frontend directory using any static server. For example:
```bash
# In a new terminal, navigate to PharmacyManagement/frontend
cd frontend
python -m http.server 3000
```
Open `http://localhost:3000` in your browser.

## Credentials
- **Admin Login**: admin@pharmacy.com / admin123
- **User Login**: rahul@gmail.com / rahul123

## Testing Instructions
1. Login as User, browse medicines, add to cart, and checkout.
2. Login as Admin, view dashboard revenue and orders. Manage medicines and users.

## API Documentation
Refer to `postman_collection.json` included in this repository.
