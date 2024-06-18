from django.urls import path, include
from . import views 
from django.urls import path
from .views import register, login_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
]



urlpatterns = [ 
    path("", views.index, name="index"),
    path("create_user", views.createUser, name="create_user"),
    path("login", views.login_view, name="login"),
    path("restaurants",views.restaurant_list,name="restaurant_list"),
    path("<string>/menu",views.restaurant_list,name="menu"),
    path('restaurant/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurant/<int:restaurant_id>/view_tables/', views.view_tables, name='view_tables'),
    path('restaurant/<int:restaurant_id>/create_reservation/', views.create_reservation, name='create_reservation'),
    path('restaurant/<int:restaurant_id>/create_feedback/', views.create_feedback, name='create_feedback'),
    path('restaurant/<int:restaurant_id>/view_feedback/', views.view_feedback, name='view_feedback'),
    path('restaurant/<int:restaurant_id>/create_promotion/', views.create_promotion, name='create_promotion'),
    path('restaurant/dining_preference/', views.dining_preference, name='dining_preference'),
    path('auth/', include('django.contrib.auth.urls')),
    path('restaurant/<int:restaurant_id>/manage-reservations/', views.manage_reservations, name='manage_reservations'),
    path('restaurant/<int:restaurant_id>/manage-reservations/<str:date>/', views.manage_reservations, name='manage_reservations_by_date'),
    path('search/', views.search_restaurants, name='search_restaurants'),
    path('tables/release/<int:table_id>/', views.release_table, name='release_table'),
    path('reservations/adjust/<int:reservation_id>/', views.adjust_reservation, name='adjust_reservation'),
    path('reservations/view_reservation/<int:reservation_id>/', views.view_reservation, name='view_reservation'),
    path('my_reservations/', views.my_reservations, name='my_reservations'),
    path('restaurant/<int:restaurant_id>/change_restaurant/', views.change_restaurant, name='change_restaurant'),
    path('restaurant/<int:restaurant_id>/upload_images/', views.upload_images, name='upload_images'),
    path('restaurant/image/<int:image_id>/delete/', views.delete_image, name='delete_image'),
    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    #Profile:
    path('profile/', views.profile_view, name='profile_view'),
    path('owner_view/', views.owner_view, name='owner_view'),
]
