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
    #Not yet used:
    path('profile/', views.profile_view, name='profile_view'),
]
