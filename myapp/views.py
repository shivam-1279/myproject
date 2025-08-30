from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import date
from .models import Category, Item, CartItem, Order, OrderItem, Reservation
from .forms import RegistrationForm, CheckoutForm

def index(request):
    featured_items = Item.objects.filter(available=True)[:3]
    categories = Category.objects.all()
    today = date.today().isoformat()

    if request.method == 'POST' and 'name' in request.POST:
        # reservation form logic ...
        pass

    context = {
        'featured_items': featured_items,
        'categories': categories,
        'today': today,
    }
    return render(request, 'index.html', context)
def menu(request):
    category_slug = request.GET.get('category')
    if category_slug:
        items = Item.objects.filter(category__slug=category_slug, available=True)
    else:
        items = Item.objects.filter(available=True)
    
    categories = Category.objects.all()
    
    context = {
        'items': items,
        'categories': categories,
    }
    return render(request, 'menu.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('myapp:index')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(item.line_total for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
    }
    return render(request, 'cart.html', context)

def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id, available=True)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        item=item,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{item.name} added to cart!')
    return redirect('myapp:menu')

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('myapp:view_cart')


def update_cart_quantity(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            return redirect('myapp:view_cart')
            
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, 'Cart updated!')
    
    return redirect('myapp:view_cart')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('myapp:menu')
    
    subtotal = sum(item.line_total for item in cart_items)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=subtotal,
                customer_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                special_instructions=form.cleaned_data['special_instructions']
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    price_at_order=cart_item.item.price
                )
            
            # Clear cart
            cart_items.delete()
            
            return redirect('myapp:order_confirmation', order_id=order.id)
    else:
        # Pre-fill form with user data if available
        initial_data = {}
        if request.user.first_name and request.user.last_name:
            initial_data['full_name'] = f"{request.user.first_name} {request.user.last_name}"
        if request.user.email:
            initial_data['email'] = request.user.email
            
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'items': cart_items,
        'subtotal': subtotal,
    }
    return render(request, 'checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})