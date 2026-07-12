from django.urls import path
import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Auth
    path('api/register', views.register),
    path('api/login', views.login),
    path('api/logout', views.logout),
    path('api/profile', views.profile),
    path('api/profile/password', views.profile_password),
    
    # Categories
    path('api/categories', views.category_list),
    path('api/categories/<str:pk>', views.category_detail),
    
    # Medicines
    path('api/medicines', views.medicine_list),
    path('api/medicines/search', views.medicine_search),
    path('api/medicines/category/<str:category>', views.medicine_by_category),
    path('api/medicines/low-stock', views.medicine_low_stock),
    path('api/medicines/<str:pk>', views.medicine_detail),
    
    # Cart
    path('api/cart', views.cart_view),
    path('api/cart/add', views.cart_add),
    path('api/cart/update', views.cart_update),
    path('api/cart/remove/<str:pk>', views.cart_remove),
    path('api/cart/clear', views.cart_clear),
    
    # Orders
    path('api/orders', views.order_list),
    path('api/orders/<str:pk>', views.order_detail),
    path('api/orders/<str:pk>/cancel', views.order_cancel),
    
    # Dashboard
    path('api/dashboard', views.dashboard_stats),
    path('api/dashboard/revenue', views.dashboard_revenue),
    path('api/dashboard/users', views.dashboard_users),
    path('api/dashboard/users/<str:pk>', views.user_delete),
    path('api/dashboard/users/<str:pk>/toggle-status', views.user_toggle_status),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
