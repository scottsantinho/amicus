from django.apps import AppConfig


# Define the configuration class for the Colloquium app
class ColloquiumConfig(AppConfig):
    # Set the default auto field for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # Set the name of the app
    name = 'colloquium'
