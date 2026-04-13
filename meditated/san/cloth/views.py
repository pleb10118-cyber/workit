from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomerSupportForm
from .models import Profile, Product, Cart, CartItem
from decimal import Decimal, InvalidOperation

# Create your views here.
@login_required
def home(request):
    return render(request, 'cloth/home.html')

@login_required
def shop(request):
    products = Product.objects.filter(active=True).select_related('seller').order_by('-created_at')
    context = {'products': products}
    return render(request, 'cloth/shop.html', context)

@login_required
def sellers(request):
    sellers = User.objects.filter(profile__is_seller=True).select_related('profile').order_by('username')
    context = {'sellers': sellers}
    return render(request, 'cloth/sellers.html', context)


@login_required
def seller_shop(request, seller_id):
    seller = get_object_or_404(User, id=seller_id, profile__is_seller=True)
    products = Product.objects.filter(seller=seller, active=True).order_by('-created_at')
    context = {'seller': seller, 'products': products}
    return render(request, 'cloth/seller_shop.html', context)

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
    cart, created = Cart.objects.get_or_create(buyer=request.user)
    items = cart.items.select_related('product').all()

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
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.is_seller:
        messages.error(request, 'Only sellers have access.')
        return redirect('home')

    if request.method == 'POST':
        sent = request.POST.get('sent')

        if sent == 'create_product':
            name = request.POST.get('name', '').strip()
            price_raw = request.POST.get('price', '0').strip()
            stock_raw = request.POST.get('stock', '0').strip()

            if not name:
                messages.error(request, 'Products need to have a name.')
                return redirect('dashboard')

            try:
                price = Decimal(price_raw)
                stock = int(stock_raw)
            except (InvalidOperation, ValueError):
                messages.error(request, 'Invalid numbers for price and stock.')
                return redirect('dashboard')

            if price < 0 or stock < 0:
                messages.error(request, 'Price and stock cannot be below 0.')
                return redirect('dashboard')

            Product.objects.create(
                seller=request.user,
                name=name,
                price=price,
                stock=stock,
                active=True,
            )
            messages.success(request, 'Product created.')
            return redirect('dashboard')

        if sent == 'update_stock':
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
                product = Product.objects.get(id=product_id, seller=request.user)
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
                return redirect('dashboard')

            product.stock = stock
            product.save(update_fields=['stock'])
            messages.success(request, f'Stock updated for {product.name}.')
            return redirect('dashboard')

    products = Product.objects.filter(seller=request.user).order_by('-created_at')
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

    if product.seller_id == request.user.id:
        messages.error(request, 'You cannot add your own product to cart.')
        return redirect('shop')

    try:
        quantity = int(request.POST.get('quantity', '1'))
    except ValueError:
        messages.error(request, 'Quantity must be a whole number.')
        return redirect('shop')

    if quantity <= 0:
        messages.error(request, 'Quantity cannot be below 0.')
        return redirect('shop')

    cart, created = Cart.objects.get_or_create(buyer=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    new_quantity = quantity if item_created else cart_item.quantity + quantity
    if new_quantity > product.stock:
        messages.error(request, "We don't have that amount in stock.")
        return redirect('shop')

    cart_item.quantity = new_quantity
    cart_item.save(update_fields=['quantity'])
    messages.success(request, f'Added {product.name} to cart.')
    return redirect('cart')


@login_required
def update_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('cart')

    try:
        cart_item = CartItem.objects.get(id=item_id, cart__buyer=request.user)
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
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
        return redirect('cart')

    if quantity > cart_item.product.stock:
        messages.error(request, "We don't have that amount in stock.")
        return redirect('cart')

    cart_item.quantity = quantity
    cart_item.save(update_fields=['quantity'])
    messages.success(request, 'Cart updated.')
    return redirect('cart')


@login_required
def remove_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('cart')

    deleted, _ = CartItem.objects.filter(id=item_id).delete()
    if deleted:
        messages.success(request, 'Item removed from cart.')
    else:
        messages.error(request, 'Cart item not found.')
    return redirect('cart')

def login_users(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
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

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.is_seller = form.cleaned_data['is_seller']
            profile.save()

            messages.success(request, 'User account was created!')
            login(request, user)
            return redirect('home')
    context = {'page': page, 'form': form}
    return render(request, 'cloth/login.html', context)