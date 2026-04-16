from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	is_seller = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user.username} ({'Seller' if self.is_seller else 'Buyer'})"


class Product(models.Model):
	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
	name = models.CharField(max_length=150)
	image = models.ImageField(upload_to='products/', blank=True, null=True)
	price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
	stock = models.PositiveIntegerField(default=0)
	active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name} ({self.stock})"


class Cart(models.Model):
	buyer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Cart({self.buyer.username})"


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
	quantity = models.PositiveIntegerField(default=1)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product')
		]

	def __str__(self):
		return f"{self.product.name} x {self.quantity}"

class CustomerSupport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer Issue from {self.user.username}"
