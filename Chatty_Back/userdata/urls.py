from django.urls import path
from .views import login, signup, verify_account, user_list_create

urlpatterns = [
    # User URLs
    path('users/login/', login, name='login'),
    path('users/signup/', signup, name='signup'),
    path('users/verification/', verify_account, name='verify_account'),
    path('users/allusers/', user_list_create, name='user-list-create'),
    ]
