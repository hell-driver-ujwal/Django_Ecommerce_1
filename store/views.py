from django.shortcuts import render, get_object_or_404
from .models import Product 
from category.models import Category
from store.models import Product

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available = True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()
 
    context = { 
         'products': products,
         'product_count':product_count,
     }
    return render(request, 'store/store.html',context)


def product_detail(request, category_slug , product_slug):
    single_product = get_object_or_404(Product, category__slug = category_slug , slug = product_slug)
    context = {
        'single_product' : single_product,
    }
    return render(request, 'store/product_detail.html', context)


#could have used this without the context_processor.py on the category app 
# def store(request):
#     categories  = Category.objects.all()
#     context = {
#         'categories': categories
#     }
#     return render(request, 'store/store.html',context)

