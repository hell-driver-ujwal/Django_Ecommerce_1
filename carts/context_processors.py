from .models import Cart , CartItem
from .views import _cart_id


# def cart_counter(request):
#     cart_count = 0 
#     if 'admin' in request.path:
#         return {}
    
#     try:
#         cart= Cart.objects.filter(cart_id =_cart_id(request)).first()
#         if cart:
#             cart_items = CartItem.objects.filter(carts=cart)
#             for cart_item in cart_items:
#                 cart_count += cart_item.quantity

#     except Cart.DoesNotExist:
#         cart_count = 0
        
#     return dict(cart_count = cart_count)


#easy peasy ,,
def cart_counter(request):
    cart_count = 0 
    if 'admin' in request.path:
        return {}

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user = request.user)
    else:
        cart_items = CartItem.objects.filter(carts__cart_id = _cart_id(request))
        
    for cart_item in cart_items:
        cart_count+=cart_item.quantity
    return dict(cart_count = cart_count)
