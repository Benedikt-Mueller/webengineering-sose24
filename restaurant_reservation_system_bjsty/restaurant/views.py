from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import *
from django import forms
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
import datetime

#Forms:
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email','password','first_name','last_name')

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=Feedback
        fields=('vote','feedback')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number','role')

class ReservationForm(forms.ModelForm):
    date = forms.DateField(required=True, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(required=True, widget=forms.widgets.TimeInput(attrs={'type': 'time'}))
    class Meta:
        model = Reservation
        fields = ['date', 'time', 'party_size', 'special_requests']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        # Verbinden der Datum- und Zeit-Informationen in ein datetime Objekt
        if date and time:
            cleaned_data['date_time'] = datetime.datetime.combine(date, time)

        return cleaned_data

    def save(self, commit=True):
        # Entfernen Sie 'date' und 'time' aus cleaned_data, da diese nicht im Modell existieren
        cleaned_data = self.cleaned_data
        date_time = cleaned_data.pop('date_time', None)

        # Überschreiben des date_time Feldes des Modells mit dem kombinierten Wert
        instance = super(ReservationForm, self).save(commit=False)
        if date_time:
            instance.date_time = date_time
        if commit:
            instance.save()
        return instance
    

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