from django.contrib import admin
from .models import Profile, Product, Cart, CartItem, CustomerSupport

# Register your models here.
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(CustomerSupport)

admin.site.site_header = "Cloth Admin"
admin.site.site_title = "Cloth Admin Portal"
admin.site.index_title = "Welcome to Cloth Administration"
