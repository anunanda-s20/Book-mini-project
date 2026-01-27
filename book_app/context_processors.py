from .models import Wishlist

def wishlist_count(request):
    # If user is logged in
    if request.user.is_authenticated:
        return {
            # Total wishlist items of the user
            'wishlist_count': Wishlist.objects.filter(user=request.user).count()
        }

    # If user is not logged in
    return {'wishlist_count': 0}
