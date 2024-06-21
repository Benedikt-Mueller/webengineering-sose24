from django.urls import path, include
from .views import *
from django.urls import path
from restaurant.views import register,login_view

app_name = 'marketing'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('customers/', customer_data_view, name='customer_data_view'),
    path('custom/', custom_data_input, name='custom_data_input'),
    path('', index_view, name='index_view'),
]