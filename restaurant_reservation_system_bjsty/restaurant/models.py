from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from .choices import Choices
import os
from django.db import models


# Models for User accounts to differentiate between
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=50, choices=Choices.ROLE_CHOICES)
    age = models.IntegerField(default=0)
    def __str__(self):
        return str(self.user) 


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.user.username

# Restaurant model
class Restaurant(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_restaurants')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=50, choices=Choices.PREFERENCE_CHOICES)
    description = models.TextField(blank=True)
    opening_hours = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)
    def __str__(self):
        return self.name
#Allow Staff to work at Restaurant
class StaffMember(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE) 
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    isManager = models.BooleanField(default=False)
# Menu model related to Restaurant
class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    def __str__(self):
        return (str(self.name)+" bei "+str(self.restaurant) + " für " + str(self.price))

# Reservation model
class Reservation(models.Model):
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reservations')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    party_size = models.IntegerField()
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Choices.STATUS_CHOICES)


    def __str__(self):
        return ("Reservation "+str(self.pk)+" at "+str(self.restaurant)+" from "+str(self.customer))
#Bilder für Restaurant:
class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='restaurants/%Y/%m/%d/')
    def delete(self, using=None, keep_parents=False):
        # Pfad zur Bilddatei
        image_path = self.image.path
        # Aufrufen der ursprünglichen Delete-Methode, um das Objekt aus der Datenbank zu entfernen
        super().delete(using=using, keep_parents=keep_parents)
        # Überprüfen, ob die Datei existiert und dann löschen
        if os.path.isfile(image_path):
            os.remove(image_path)
    
# Review and Rating model
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()
    comments = models.TextField(blank=True)

# Promotion and Loyalty Program model
class Promotion(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='promotions')
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    discount_rate = models.FloatField()
    loyality = models.IntegerField(default=0) #Legt fest, wie oft die Kunden bereits in einem Restaurant gegessen haben müssen, damit sie als loyal gelten (aktuell wird die Anzahl alter Reservierungen geprüft)

    def __str__(self):
        return ("Promotion \"" + str(self.title) + "\" at "+str(self.restaurant))

# Table model for managing table availability
class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    is_reserved = models.BooleanField(default=False)
    def __str__(self):
        return (str(self.restaurant) + " Tisch: " + str(self.pk) + "mit Kapazität " +str(self.capacity))

# Model for managing dining preferences and feedback for trend analysis
class DiningPreference(models.Model):
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    preferences = models.CharField(max_length=50, choices=Choices.PREFERENCE_CHOICES)
    def __str__(self):
        return (str(self.preferences)+ " von " + str(self.customer))

class Feedback(models.Model):
    customer = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    vote = models.CharField(max_length=10, choices=Choices.VOTE_CHOICES)
    feedback = models.TextField(blank=True)
    def __str__(self):
        return ("Bewertung für " + str(self.restaurant) + " von " + str(self.customer))