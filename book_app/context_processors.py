# book_app/context_processors.py

from .models import Wishlist  # Import Wishlist model

def wishlist_count(request):
    # This function will run for every request (if added in settings)

    # If user is logged in
    if request.user.is_authenticated:
        return {
            # Count how many wishlist items this user has
            'wishlist_count': Wishlist.objects.filter(user=request.user).count()
        }

    # If user is not logged in, return 0
    return {'wishlist_count': 0}
