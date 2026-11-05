from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Product, Category, HomepageSection, HomepageContent, User, Cart, CartItem
from django.db.models import Q

def home(request):
    showcase_products = []
    for cat in ['shoes', 'perfumes', 'makeup', 'skincare']:
        prod = Product.objects.filter(category__name=cat, is_featured=True).first()
        if not prod:
            prod = Product.objects.filter(category__name=cat).first()
        if prod:
            showcase_products.append(prod)

    sections = {
        'shoes': HomepageSection.objects.filter(section_name='shoes').first(),
        'perfumes': HomepageSection.objects.filter(section_name='perfumes').first(),
        'skincare': HomepageSection.objects.filter(section_name='skincare').first(),
        'makeup': HomepageSection.objects.filter(section_name='makeup').first(),
    }

    hero_content = HomepageContent.objects.first()

    context = {
        'showcase_products': showcase_products,
        'sections': sections,
        'hero': hero_content,
    }
    return render(request, 'Dior/index.html', context)

def shoes(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(category__name='shoes')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'Dior/Heels.html', {'products': products, 'query': query})

def perfumes(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(category__name='perfumes')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'Dior/Parfums.html', {'products': products, 'query': query})

def makeup(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(category__name='makeup')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'Dior/makeup.html', {'products': products, 'query': query})

def skincare(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(category__name='skincare')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'Dior/Skincare.html', {'products': products, 'query': query})

def search_results(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    return render(request, 'Dior/search.html', {'products': products, 'query': query})

def collections(request):
    sections = {
        'shoes': HomepageSection.objects.filter(section_name='shoes').first(),
        'perfumes': HomepageSection.objects.filter(section_name='perfumes').first(),
        'skincare': HomepageSection.objects.filter(section_name='skincare').first(),
        'makeup': HomepageSection.objects.filter(section_name='makeup').first(),
    }
    context = {
        'sections': sections,
    }
    return render(request, 'Dior/product.html', context)

def auth_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'login':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user_obj = User.objects.filter(Q(email=email) | Q(username=email)).first()
            
            if user_obj is not None and user_obj.check_password(password):
                login(request, user_obj)
                messages.success(request, f'Welcome back, {user_obj.first_name or user_obj.username}!')
                return redirect('home_url')
            else:
                messages.error(request, 'Invalid email/username or password.')
                return redirect('auth_url')

        elif form_type == 'signup':
            full_name = request.POST.get('name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')

            if password != password2:
                messages.error(request, 'Passwords do not match.')
                return redirect('auth_url')

            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                messages.error(request, 'Username or Email already exists.')
                return redirect('auth_url')

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name
            )
            user.save()
            
            login(request, user)
            messages.success(request, f'Welcome, {full_name}! Your account has been created.')
            return redirect('home_url')
            
    return render(request, 'Dior/login_register.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home_url')

def about_view(request):
    return render(request, 'Dior/about.html')


def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = _get_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'"{product.name}" added to cart.')
        return redirect(request.META.get('HTTP_REFERER', 'home_url'))
    return redirect('home_url')


def cart_view(request):
    cart = _get_cart(request)
    items = cart.items.all()
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'Dior/cart.html', context)


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart_url')


def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id)
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            item.quantity = new_quantity
            item.save()
        else:
            item.delete()
        messages.success(request, 'Cart updated.')
    return redirect('cart_url')

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'Dior/detail.html', context)