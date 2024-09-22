# Import the path function from django.urls module
from django.urls import path
# Import the auth_views from django.contrib.auth module
from django.contrib.auth import views as auth_views
# Import the LogoutView from django.contrib.auth.views module
from django.contrib.auth.views import LogoutView
# Import views from the current directory
from . import views

# Define the URL patterns for the nucleus app
urlpatterns = [
    # URL pattern for the home page
    path('', views.home, name='home'),
    # URL pattern for the login page, using Django's built-in LoginView
    path('login/', auth_views.LoginView.as_view(template_name='nucleus/login.html'), name='login'),
    # URL pattern for the logout functionality, using Django's built-in LogoutView
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    # URL pattern for the user profile page
    path('profile/', views.profile, name='profile'),
    # URL pattern for the signup page
    path('signup/', views.signup, name='signup'),  # Add this line
]
