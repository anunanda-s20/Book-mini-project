# book_app/apps.py

from django.apps import AppConfig  # Import Django's base AppConfig class

class BookAppConfig(AppConfig):  # Configuration class for this app

    # Sets the default primary key type for models (auto-increment ID)
    default_auto_field = 'django.db.models.BigAutoField'

    # Name of the app
    name = 'book_app'

    # This method runs once when Django starts
    def ready(self):
        # Import signals file so Django registers signal functions at startup
        import book_app.signals
