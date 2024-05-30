from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import *
from django import forms
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import *
import datetime

# views:
def index(request):
    return HttpResponse("Guten Tag. Sie befinden sich auf der Hauptseite dieses Restaurant-Reservierungssystems!")

def createUser(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.password = make_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('login')  # Angenommen, es existiert eine Login-Seite.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'restaurant/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def login(request):
    return HttpResponse("Login not yet implemented!")

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurant/restaurant_list.html', {'restaurants': restaurants})

def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_items = Menu.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/menu.html', {'restaurant': restaurant, 'menu_items': menu_items})

def view_tables(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/tables.html', {'restaurant': restaurant, 'tables': tables})

@login_required
def create_reservation(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.restaurant = restaurant
            reservation.customer = request.user.userprofile  # Vorausgesetzt der User ist eingeloggt
            reservation.status = 'pending'
            reservation.save()
            return redirect('restaurant_list')  # Angenommen, Sie haben eine URL für Reservierungserfolg
    else:
        form = ReservationForm()
    return render(request, 'restaurant/create_reservation.html', {'form': form, 'restaurant': restaurant})

@login_required
def profile_view(request):
    userprofile = get_object_or_404(UserProfile, user = request.user)
    diningPreferences = DiningPreference.objects.filter(customer=userprofile)
    return render(request, 'restaurant/profile_view.html', {'user':request.user, 'userprofile':userprofile,'preferences':diningPreferences })

@login_required
def create_feedback(request, restaurant_id):
    userprofile = get_object_or_404(UserProfile, user = request.user)
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.restaurant=restaurant
            feedback.customer=userprofile
            feedback.save()
            return redirect('restaurant_list')
    else:
        form = FeedbackForm
        return render(request, 'restaurant/create_feedback.html', {'form': form, 'restaurant': restaurant})    
def view_feedback(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    feedbacks = Feedback.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/view_feedback.html',({'feedbacks':feedbacks, 'restaurant':restaurant}))

def create_promotion(request,restaurant_id):
    restaurant = get_object_or_404(Restaurant,pk=restaurant_id)
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.restaurant=restaurant
            promotion.save()
            return redirect('restaurant_list')
        else:
            return render(request, 'restaurant/create_promotion.html', {
                'form': form,
                'restaurant': restaurant
            })
    else:
        form = PromotionForm
        return render(request, 'restaurant/create_promotion.html', {'form': form, 'restaurant': restaurant}) 
    
@login_required
def dining_preference(request):
       user_profile = UserProfile.objects.get(user=request.user)

       if request.method == 'POST':
           form = DiningPreferenceForm(request.POST)
           if form.is_valid():
               selected_preferences = form.cleaned_data['preferences']
               # Lösche alle bestehenden Präferenzen, um sie durch die neuen Auswahlmöglichkeiten zu ersetzen.
               user_profile.diningpreference_set.clear()
               for preference in selected_preferences:
                   DiningPreference.objects.create(customer=user_profile, preferences=preference.preferences)
               return redirect('success_url')  # URL nach Erfolg anpassen
       else:
           form = DiningPreferenceForm()
           # Optional: Vorauswahlen basierend auf existierenden Präferenzen des Benutzers
           form.fields['preferences'].initial = user_profile.diningpreference_set.all()

       return render(request, 'restaurant/manage_preferences.html', {'form': form})