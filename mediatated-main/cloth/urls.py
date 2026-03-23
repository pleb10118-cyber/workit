from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('retailers/', views.retailers, name='retailers'),
    path('account/', views.account, name='account'),
    path('support/', views.support, name='support'),
    path('cart/', views.cart, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove-cart-item'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_users, name='login'),
    path('logout/', views.logout_users, name='logout'),
    path('register/', views.register_users, name='register'),
]