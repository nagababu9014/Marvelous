from cart.models import Cart, CartItem
from orders.models import Order


from cart.models import Cart
from orders.models import Order


def get_cart(user=None, guest_id=None, create=False):
    """
    Rules:
    - Cart is ALWAYS allowed
    - Orders NEVER block cart
    - Empty cart is valid
    """

    # ✅ AUTHENTICATED USER
    if user and user.is_authenticated:
        cart = Cart.objects.filter(user=user).first()
        if not cart and create:
            cart = Cart.objects.create(user=user)
        return cart

    # ✅ GUEST USER
    if guest_id:
        cart = Cart.objects.filter(guest_id=guest_id).first()
        if not cart and create:
            cart = Cart.objects.create(guest_id=guest_id)
        return cart

    return None


def merge_guest_cart_to_user(guest_id, user):
    print("MERGING CART FOR GUEST:", guest_id)
    if not guest_id or not user:
        return

    guest_cart = Cart.objects.filter(guest_id=guest_id).first()
    if not guest_cart:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for item in guest_cart.items.all():
        user_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=item.product,
            defaults={"quantity": item.quantity},
        )
        if not created:
            user_item.quantity += item.quantity
            user_item.save()

    # 🔥 Remove guest cart after merge
    guest_cart.delete()
