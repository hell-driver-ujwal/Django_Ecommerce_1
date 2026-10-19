from django.shortcuts import render, get_object_or_404
from .models import Product 
from category.models import Category
from store.models import Product
from carts.models import CartItem , Cart
from carts.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q


# Create your views here.

def store(request, category_slug=None):

    products = Product.objects.filter(is_available = True)
    
    if category_slug is not  None:
        categories = get_object_or_404(
            Category, 
            slug = category_slug)
        products = products.filter(category = categories)

    products = products.order_by('-created_date')

    # for paginator 
    paginator = Paginator(products,9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = { 
         'product_count': paginator.count,
         'page_obj':page_obj,
         'is_search':False,
     }   
    return render(request, 'store/store.html',context)

def product_detail(request, category_slug , product_slug ):
    try:
        single_product = Product.objects.get(category__slug = category_slug , slug = product_slug)
        in_cart = CartItem.objects.filter(carts__cart_id = _cart_id(request), product = single_product).exists()
    except Exception as e:
        raise e 
    
    context = {
        'single_product' : single_product,
        'in_cart': in_cart
    }
    return render(request, 'store/product_detail.html', context)


# my version of search ,
def search(request):
    keyword = request.GET.get('keyword', '').strip()
    products = Product.objects.none()
    query = Q()

    if keyword:
        for word  in keyword.split():
            query &= (Q(product_name__icontains = word) |
            Q(description__icontains = word) )

        products = Product.objects.filter(query) 
    
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context ={
             'page_obj': page_obj,
             'product_count': paginator.count,
             'keyword': keyword,
             'is_search' : True 
        }   
    
    return render(request, 'store/store.html', context)

    


#could have used this without the context_processor.py on the category app 
# def store(request):
#     categories  = Category.objects.all()
#     context = {
#         'categories': categories
#     }
#     return render(request, 'store/store.html',context)

