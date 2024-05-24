from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Guten Tag. Sie befinden sich auf der Hauptseite dieses Restaurant-Reservierungssystems!")
def createUser(request):
    return HttpResponse("Erstellen sie einen Benutzer!")