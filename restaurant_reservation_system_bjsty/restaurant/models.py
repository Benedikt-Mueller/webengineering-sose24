from django.db import models
from django.contrib.auth.models import User

# Models for User accounts to differentiate between
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('owner', 'Restaurant Owner'),
        ('staff', 'Restaurant Staff'),
        ('admin', 'System Administrator'),
        ('developer', 'Developer'),
        ('marketing', 'Marketing Team Member'),
    )  
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    def __str__(self):
        return str(self.user)
    

# Restaurant model
class Restaurant(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_restaurants')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    opening_hours = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    def __str__(self):
        return self.name

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
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return ("Reservation "+str(self.pk)+" at "+str(self.restaurant)+" from "+str(self.customer))

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
    is_available = models.BooleanField(default=True)
    def __str__(self):
        return (str(self.restaurant) + " Tisch: " + str(self.pk))

# Model for managing dining preferences and feedback for trend analysis
class DiningPreference(models.Model):
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    PREFERENCE_CHOICES = (
        ('international' , 'Internationale Küche'),
        ('german' , 'Deutsche Küche'),
        ('danish' , 'Dänische Küche'),
        ('italian' , 'Italienische Küche'),
        ('american' , 'Amerikanische Küche'),
        ('indian' , 'Indische Küche'),
        ('asian' , 'Asiatische Küche'),
    )
    preferences = models.CharField(max_length=50, choices=PREFERENCE_CHOICES)
    def __str__(self):
        return (str(self.preferences)+ " von " + str(self.customer))

class Feedback(models.Model):
    customer = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    VOTE_CHOICES = (
        ('one_star', '1/5'),
        ('two_star', '2/5'),
        ('three_star', '3/5'),
        ('four_star', '4/5'),
        ('five_star', '5/5'),
    )
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)
    feedback = models.TextField(blank=True)
    def __str__(self):
        return ("Bewertung für " + str(self.restaurant) + " von " + str(self.customer))
# Implementierung der Suchfunktion
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name  # Gibt den Namen des Restaurants zurück, nützlich für die Admin-Ansicht und Log-Dateien.    