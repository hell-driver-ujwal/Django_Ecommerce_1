from django.contrib import admin
from .models import Order, Payment, OrderProduct
# Register your models here.

class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['payment', 'user', 'product', 'quantity', 'product_price', 'ordered']
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'full_name',
        'email',
        'phone_number',
        'country',
        'city',
        'order_total',
        'tax',
        'status',
        'ip',
        'is_ordered',
    ]
    list_filter =[
        'status',
        'is_ordered',
    ]
    search_fields =[
        'order_number', 'first_name','phone_number','email'
    ]
    list_per_page = 20 
    inlines = [OrderProductInLine]

admin.site.register(Order, OrderAdmin)

admin.site.register(OrderProduct)

admin.site.register(Payment)