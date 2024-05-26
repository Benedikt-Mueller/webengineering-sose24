from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import UserProfile, Restaurant
from django import forms
from django.http import HttpResponse

#Forms:
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email','password','first_name','last_name')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number','role')

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