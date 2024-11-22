from django.urls import path
from .views import login, signup, verify_account, password_reset_request, password_reset_confirm

urlpatterns = [
    # User URLs
    path('users/login/', login, name='login'),
    path('users/signup/', signup, name='signup'),
    path('users/verification/', verify_account, name='verify_account'),
    path('users/password_reset_request/<str:rqemail>/', password_reset_request, name='password_reset_request'),
    path('users/password_reset/<str:user_id>/', password_reset_confirm, name='password_reset_request'),
    ]
