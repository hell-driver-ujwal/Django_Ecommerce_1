from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Product, Variations
from .models import Cart, CartItem


def _cart_id(request):
    """Return the current visitor's session key, creating it if necessary."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@require_POST
def add_cart(request, product_id):
    """Add one unit of the selected product/variation combination."""
    product = get_object_or_404(Product, id=product_id)
    product_variations = []

    # The product-detail form sends the chosen color and size.
    # The cart's + button sends the same values in hidden inputs.
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

    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(
        product=product,
        carts=cart,
    ).prefetch_related("variations")

    selected_ids = {variation.id for variation in product_variations}
    matching_item = None

    for item in cart_items:
        existing_ids = {variation.id for variation in item.variations.all()}
        if existing_ids == selected_ids:
            matching_item = item
            break

    if matching_item is not None:
        matching_item.quantity += 1
        matching_item.save(update_fields=["quantity"])
    else:
        matching_item = CartItem.objects.create(
            product=product,
            carts=cart,
            quantity=1,
        )
        matching_item.variations.set(product_variations)

    return redirect("cart")


@require_POST
def remove_cart(request, cart_item_id):
    """Decrease the quantity of one specific cart item."""
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
