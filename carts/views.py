from django.shortcuts import render , redirect
from store.models import Product
from .models import Cart , CartItem
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _cart_id(request):
    cart_s = request.session.session_key
    if not cart_s:
        cart_s = request.session.create()
    return cart_s

def add_cart(request, product_id):
    product = get_object_or_404(Product, id = product_id) #get the product 
    try:
        cart = Cart.objects.get(cart_id= _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    try:
        cart_item = CartItem.objects.get(product = product, carts = cart)
        if cart_item.quantity < product.stock :
            cart_item.quantity +=1 
            cart_item.save()

# for sneaky guys 
    except CartItem.DoesNotExist:
        if product.stock > 0:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                carts = cart,
            )
            cart_item.save()
        else:
            pass
    return redirect('cart')

def remove_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        cart =  get_object_or_404(Cart, cart_id = _cart_id(request))
        cart_item = get_object_or_404(CartItem, product = product, carts = cart)

    except(Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    if cart_item.quantity > 1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def delete_cart_item(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    try:
        cart =  get_object_or_404(Cart, cart_id = _cart_id(request))
        cart_item = get_object_or_404(CartItem, product = product, carts = cart)

    except(Cart.DoesNotExist, CartItem.DoesNotExist):
            pass
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity =0, cart_items = None, tax =0, grand_total = 0):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(carts = cart, is_active = True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2* total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request, 'store/cart.html', context)

