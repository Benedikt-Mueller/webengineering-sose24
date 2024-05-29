from django.urls import path, include
from . import views 

urlpatterns = [ 
    path("", views.index, name="index"),
    path("create_user", views.createUser, name="create_user"),
    #path("login", views.login, name="login"),
    path("restaurants",views.restaurant_list,name="restaurant_list"),
    path("<string>/menu",views.restaurant_list,name="menu"),
    path('restaurant/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurant/<int:restaurant_id>/tables/', views.view_tables, name='restaurant_tables'),
    path('restaurant/<int:restaurant_id>/create_reservation/', views.create_reservation, name='create_reservation'),
    path('restaurant/<int:restaurant_id>/create_feedback/', views.create_feedback, name='create_feedback'),
    path('restaurant/<int:restaurant_id>/view_feedback/', views.view_feedback, name='view_feedback'),
    path('auth/', include('django.contrib.auth.urls')),
    #Not yet used:
    path('profile/', views.profile_view, name='profile_view'),
]
