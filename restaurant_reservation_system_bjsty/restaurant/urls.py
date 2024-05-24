from django.urls import path 
from . import views 

urlpatterns = [ 
    path("", views.index, name="index"),
    path("create_user", views.createUser, name="create_user")
]
