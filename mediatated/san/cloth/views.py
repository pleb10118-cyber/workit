from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomerSupportForm
from .models import Profile, Product, Cart, CartItem, CustomerSupport
from decimal import Decimal, InvalidOperation

# Create your views here.
@login_required
def home(request):
    return render(request, 'cloth/home.html')

@login_required
def shop(request):
    products = Product.objects.filter(active=True).select_related('retailer').order_by('-created_at')
    context = {'products': products}
    return render(request, 'cloth/shop.html', context)

@login_required
def retailers(request):
    return render(request, 'cloth/retailers.html')

@login_required
def account(request):
    user = request.user
    username = request.POST.get('username', '').strip()
    first_name = request.POST.get('first_name','').strip()
    last_name = request.POST.get('last_name','').strip()
    email = request.POST.get('email','').strip()

    if request.method == 'POST':
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        messages.success(request, 'Account updated successfully.')
        return redirect('account')

    return render(request, 'cloth/account.html')

@login_required
def support(request):
    if request.method == 'POST':
        form = CustomerSupportForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.save()
            messages.success(request, 'Thank you for reporting your issue!')
            return redirect('support')
    else:
        form = CustomerSupportForm()
    return render(request, 'cloth/support.html', {'form': form})

@login_required
def cart(request):
    cart_obj, created = Cart.objects.get_or_create(buyer=request.user)
    items = cart_obj.items.select_related('product').all()

    cart_items = []
    total = Decimal('0.00')
    for item in items:
        item_total = item.product.price * item.quantity
        total += item_total
        cart_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'item_total': item_total,
            'item_id': item.id
        })

    context = {'cart_items': cart_items, 'total': total}
    return render(request, 'cloth/cart.html', context)

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if not profile.is_retailer:
        messages.error(request, 'Retailer access only.')
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_product':
            name = request.POST.get('name', '').strip()
            price_raw = request.POST.get('price', '0').strip()
            stock_raw = request.POST.get('stock', '0').strip()

            if not name:
                messages.error(request, 'Product name is required.')
                return redirect('dashboard')

            try:
                price = Decimal(price_raw)
                stock = int(stock_raw)
            except (InvalidOperation, ValueError):
                messages.error(request, 'Use valid numbers for price and stock.')
                return redirect('dashboard')

            if price < 0 or stock < 0:
                messages.error(request, 'Price and stock cannot be below 0.')
                return redirect('dashboard')

            Product.objects.create(
                retailer=request.user,
                name=name,
                price=price,
                stock=stock,
                active=True,
            )
            messages.success(request, 'Product created.')
            return redirect('dashboard')

        if action == 'update_stock':
            product_id = request.POST.get('product_id')
            stock_raw = request.POST.get('stock', '0').strip()
            try:
                stock = int(stock_raw)
            except ValueError:
                messages.error(request, 'Stock must be a whole number.')
                return redirect('dashboard')

            if stock < 0:
                messages.error(request, 'Stock cannot be below 0.')
                return redirect('dashboard')

            try:
                product = Product.objects.get(id=product_id, retailer=request.user)
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
                return redirect('dashboard')

            product.stock = stock
            product.save(update_fields=['stock'])
            messages.success(request, f'Stock updated for {product.name}.')
            return redirect('dashboard')

    products = Product.objects.filter(retailer=request.user).order_by('-created_at')
    context = {'products': products}
    return render(request, 'cloth/dashboard.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('shop')

    try:
        product = Product.objects.get(id=product_id, active=True)
    except Product.DoesNotExist:
        messages.error(request, 'Item not found.')
        return redirect('shop')

    try:
        quantity = int(request.POST.get('quantity', '1'))
    except ValueError:
        messages.error(request, 'Quantity must be a whole number.')
        return redirect('shop')

    if quantity <= 0:
        messages.error(request, 'Quantity must be greater than 0.')
        return redirect('shop')

    cart_obj, created = Cart.objects.get_or_create(buyer=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)

    new_quantity = quantity if created else item.quantity + quantity
    if new_quantity > product.stock:
        messages.error(request, 'Not enough stock for that quantity.')
        return redirect('shop')

    item.quantity = new_quantity
    item.save(update_fields=['quantity'])
    messages.success(request, f'Added {product.name} to cart.')
    return redirect('cart')


@login_required
def update_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('cart')

    try:
        item = CartItem.objects.select_related('product', 'cart').get(id=item_id, cart__buyer=request.user)
    except CartItem.DoesNotExist:
        messages.error(request, 'Cart item not found.')
        return redirect('cart')

    try:
        quantity = int(request.POST.get('quantity', '1'))
    except ValueError:
        messages.error(request, 'Quantity must be a whole number.')
        return redirect('cart')

    if quantity < 0:
        messages.error(request, 'Quantity cannot be below 0.')
        return redirect('cart')

    if quantity == 0:
        item.delete()
        messages.success(request, 'Item removed from cart.')
        return redirect('cart')

    if quantity > item.product.stock:
        messages.error(request, 'Quantity exceeds current stock.')
        return redirect('cart')

    item.quantity = quantity
    item.save(update_fields=['quantity'])
    messages.success(request, 'Cart updated.')
    return redirect('cart')


@login_required
def remove_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('cart')

    deleted, details = CartItem.objects.filter(id=item_id, cart__buyer=request.user).delete()
    if deleted:
        messages.success(request, 'Item removed from cart.')
    else:
        messages.error(request, 'Cart item not found.')
    return redirect('cart')

def login_users(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            Profile.objects.get_or_create(user=user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password is incorrect')
    return render(request, 'cloth/login.html')

def logout_users(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def register_users(request):
    page = 'register'
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.is_retailer = form.cleaned_data['is_retailer']
            profile.save()

            messages.success(request, 'User account was created!')
            login(request, user)
            return redirect('home')
    context = {'page': page, 'form': form}
    return render(request, 'cloth/login.html', context)