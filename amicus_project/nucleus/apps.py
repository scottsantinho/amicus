# Import the AppConfig class from django.apps module
from django.apps import AppConfig


# Define the NucleusConfig class that inherits from AppConfig
class NucleusConfig(AppConfig):
    # Set the default auto field for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # Set the name of the app
    name = 'nucleus'
