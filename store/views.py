from django.shortcuts import render, get_object_or_404, redirect
from .models import Product 
from category.models import Category
from store.models import Product
from carts.models import CartItem , Cart
from carts.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required
from .forms import ReviewForms, ReviewRatings
from orders.models import OrderProduct 
from django.contrib import messages

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
       # in_cart = CartItem.objects.filter(carts__cart_id = _cart_id(request), product = single_product).exists()
        reviews = ReviewRatings.objects.filter(product = single_product, status = True).select_related('user').order_by('-created_at')
    except Exception as e:
        raise e 
    
    context = {
        'single_product' : single_product,
        #'in_cart': in_cart,
        'reviews':reviews
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

@require_POST
@login_required
def add_review(request, product_id):

    user = request.user
    product = get_object_or_404(Product, id=product_id)

    order_product = OrderProduct.objects.filter(
        user=user,
        product=product,
        ordered=True
    ).first()

    if order_product:

        form = ReviewForms(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.product = product
            review.user = user
            review.ip = request.META.get('REMOTE_ADDR', '')

            review.save()

            messages.success(
                request,
                "You have successfully added a review"
            )

        else:
            messages.error(
                request,
                "There is something wrong with your review"
            )

    else:
        messages.error(
            request,
            "You have to buy the product to add a review"
        )

    return redirect(product.get_url())



@require_POST 
@login_required
def remove_review(request, review_id):
    user = request.user
    review = get_object_or_404(ReviewRatings, user = user, id = review_id)
    produt_url = review.product.get_url()

    review.delete()
    return redirect(produt_url)


@require_POST 
@login_required
def edit_review(request, review_id):
    user = request.user
    review = get_object_or_404(ReviewRatings, user = user, id = review_id)
    produt_url = review.product.get_url()


    # instance=review this shit is fire 
    form = ReviewForms(request.POST, instance=review)
    if form.is_valid():
        edited_review = form.save(commit=False)
        edited_review.is_edited = True
        edited_review.save()

        messages.success(request, "Review updated successfully.")
    else:
        messages.error(request, "Invalid review information.")

    return redirect(produt_url)
    
    

    
