from django.shortcuts import render
from django.http import HttpResponse
from carts.models import CartItem
from django.shortcuts import redirect
from .forms import OrderForm, Order
import datetime
# Create your views here.

def payments(request):
    return render(request, 'orders/payments.html')


def place_order(request, total = 0, quantity = 0):
    curent_user = request.user
    cart_items = CartItem.objects.filter(user = curent_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
 
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total = (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2* total)/100
    grand_total = total + tax


    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():

            data = Order()
            data.user = curent_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone_number = form.cleaned_data['phone_number']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']

            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')

            # Save first to generate the primary key
            data.save()

            # Generate the order number
            current_date = datetime.date.today().strftime('%Y%m%d')
            order_number = current_date + str(data.id)

            data.order_number = order_number
            data.save(update_fields=['order_number'])


            order = Order.objects.get(user = curent_user, is_ordered = False, order_number = order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'tax':tax,
                'total':total,
                'grand_total': grand_total
            }
            return render(request, 'orders/payments.html', context= context)
    

