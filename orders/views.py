from django.shortcuts import render
from django.http import HttpResponse
from carts.models import CartItem
from django.shortcuts import redirect
from .forms import OrderForm, Order
import datetime
import json
from django.views.decorators.http import require_POST
from .models import Payment , OrderProduct , Product



# for email 
# Verification
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

#  for json
import json
from django.http import JsonResponse

# for decorator
from django.views.decorators.http import require_POST


@require_POST
def payments(request):
    try:
        body = json.loads(request.body)
        order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderID'])
    except (ValueError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )
    # Store transcations details into payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # move cart_items to order product table 
    cart_items = CartItem.objects.filter(user = request.user, )

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id 
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variations = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id = orderproduct.id)
        orderproduct.variation.set(product_variations)

        orderproduct.save()

        # Redcuing the quantity so the sold procuct 

        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()
    # Clear cart 
    CartItem.objects.filter(user = request.user).delete()

    user = request.user
    email = user.email
    mail_subject = "Thank you for your order"
    message = render_to_string('orders/order_recived_email.html',{
        'user': user,
        'order':order,
        })
    
    to_email = email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order id and transaction id back to sendData method via JSON Resposnse 
    data = {
        'order_number':order.order_number,
        'transID': payment.payment_id ,
    }

    return JsonResponse(data)



@require_POST
def place_order(request, total = 0, quantity = 0):
    curent_user = request.user
    cart_items = CartItem.objects.filter(user = curent_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
 
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2* total)/100
    grand_total = total + tax

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
    
    # This runs only when the form is INVALID
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number = order_number, is_ordered = True)
        order_products = OrderProduct.objects.filter(order_id = order.id)
        subtotal = 0
        for i in order_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id = transID)
        context ={
            'order':order,
            'order_number':order_number,
            'order_products':order_products,
            'payment_id':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
        }

        return render(request, 'orders/order_complete.html', context)
    
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')