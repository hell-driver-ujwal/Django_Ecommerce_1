from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.contrib import messages
from store.models import Product, Variations
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required


def _cart_id(request):
    """Return the current visitor's session key, creating it if necessary."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Sum

from store.models import Product, Variations
from carts.models import Cart, CartItem


@require_POST
def add_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # 1. Get selected variations
    product_variations = []

    for key, value in request.POST.items():
        if key not in ("color", "size"):
            continue

        variation = get_object_or_404(
            Variations,
            product=product,
            variations_category__iexact=key,
            variation_value__iexact=value.strip(),
            is_active=True,
        )

        product_variations.append(variation)

    # 2. Identify the user's cart items
    if request.user.is_authenticated:

        cart_items = CartItem.objects.filter(
            user=request.user,
            product=product,
            is_active=True
        ).prefetch_related("variations")

    else:

        cart, _ = Cart.objects.get_or_create(
            cart_id=_cart_id(request)
        )

        cart_items = CartItem.objects.filter(
            carts=cart,
            product=product,
            is_active=True
        ).prefetch_related("variations")

    # 3. Calculate quantity already in cart
    quantity_in_cart = (
        cart_items.aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    # 4. Check stock
    if not product.is_available or quantity_in_cart >= product.stock:

        messages.error(
            request,
            f"Sorry, only {product.stock} units are in stock."
        )
        return redirect("cart")

    # 5. Find matching variation combination
    selected_ids = {
        variation.id for variation in product_variations
    }

    matching_item = None

    for item in cart_items:

        existing_ids = {
            variation.id
            for variation in item.variations.all()
        }

        if existing_ids == selected_ids:
            matching_item = item
            break

    # 6. Update existing item
    if matching_item is not None:

        matching_item.quantity += 1
        matching_item.save(update_fields=["quantity"])

    # 7. Create new item
    else:

        if request.user.is_authenticated:

            # Reuse a cart associated with user's items,
            # or create a cart for this session.
            existing_item = CartItem.objects.filter(
                user=request.user
            ).first()

            if existing_item:
                cart = existing_item.carts
            else:
                cart, _ = Cart.objects.get_or_create(
                    cart_id=_cart_id(request)
                )

            matching_item = CartItem.objects.create(
                user=request.user,
                product=product,
                carts=cart,
                quantity=1
            )

        else:

            matching_item = CartItem.objects.create(
                product=product,
                carts=cart,
                quantity=1
            )

        matching_item.variations.set(
            product_variations
        )

    return redirect("cart")



@require_POST
def remove_cart(request, cart_item_id):
    """Decrease the quantity of one specific cart item."""
    if request.user.is_authenticated:
        cart_item = get_object_or_404(
                CartItem,
                id=cart_item_id,
                user = request.user,
                is_active=True,
            )

    else:
        cart_item = get_object_or_404(
            CartItem,
            id=cart_item_id,
            carts__cart_id=_cart_id(request),
            is_active=True,
        )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save(update_fields=["quantity"])
    else:
        cart_item.delete()

    return redirect("cart")


@require_POST
def delete_cart_item(request, cart_item_id):
    """Remove one specific cart item, regardless of quantity."""
    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        carts__cart_id=_cart_id(request),
        is_active=True,
    )
    cart_item.delete()
    return redirect("cart")


def cart(request):
    """Display the current visitor's cart and its totals."""
    total = 0
    quantity = 0
    cart_items = CartItem.objects.none()

    if request.user.is_authenticated:
            cart_items = (
                CartItem.objects.filter(user = request.user, is_active = True)
                .select_related("product")
                .prefetch_related("variations")
            )            
    else:
        current_cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        if current_cart is not None:
            cart_items = (
                CartItem.objects.filter(carts=current_cart, is_active=True)
                .select_related("product")
                .prefetch_related("variations")
            )

    for item in cart_items:
        total += item.product.price * item.quantity
        quantity += item.quantity

    tax = Decimal(total) * Decimal("0.02")
    grand_total = Decimal(total) + tax

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, "store/cart.html", context)



@login_required(login_url='login')
def checkout(request):
    """Display authenticated user's cart and totals."""

    total = 0
    quantity = 0

    cart_items = (
        CartItem.objects.filter(
            user=request.user,
            is_active=True
        )
        .select_related("product")
        .prefetch_related("variations")
    )

    for item in cart_items:
        total += item.product.price * item.quantity
        quantity += item.quantity

    tax = Decimal(total) * Decimal("0.02")
    grand_total = Decimal(total) + tax

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }

    return render(request, "store/checkout.html", context)
