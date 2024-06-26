from django.shortcuts import render, redirect, get_object_or_404
from .functions import * #Erlaub Zugriff auf die ausgelagerten Funktionen
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

#Die Statistiken dieses Marketing-Moduls verwenden Matplotlib, Pandas und Seaborn, da wir diese Module auch im Kurs "Data Science" verwenden und damit vertraut sind. Außerdem können Performanceprobleme auf Clientseite so ausgeschlossen werden,
#die bei JavaScript gegebenenfalls auftreten können. Die Statistiken werden über ausgelagerte Methoden als Bild generiert und anschließend im Template geladen. 

@login_required
def customer_data_view(request):
    #Zugriff prüfen:
    currentUser = get_object_or_404(UserProfile, user=request.user)
    if(currentUser.role != 'owner' and currentUser.role != 'developer' and currentUser.role != 'marketing' and currentUser.role != 'admin'):
         return HttpResponseForbidden("Zugriff verweigert: Sie verfügen nicht über die nötige Berechtigung, um dieses System zu nutzen!") 
    
    #Statistiken erstellen (bei Performanceproblemen sollte man diesen Schritt zeitgestuert als Cronjob [oder Windows-Equivalent] ausführen, aber dann können Daten veraltet sein):
    generateAgePlot()
    generateReservationGraph()
    generateTimeslotGraph()
    generateDiningPreferencePlot()
    generateSeasonGraph()
    generateFeedbackPlot()
    #Template anzeigen:++
    return render(request, 'marketing/customer_data.html')

@login_required
def custom_data_input(request):
    #Zugriff prüfen:
    currentUser = get_object_or_404(UserProfile, user=request.user)
    if(currentUser.role != 'owner' and currentUser.role != 'developer' and currentUser.role != 'marketing' and currentUser.role != 'admin'):
         return HttpResponseForbidden("Zugriff verweigert: Sie verfügen nicht über die nötige Berechtigung, um dieses System zu nutzen!") 
     
    #Eigentliche Funktion:
    if request.method == 'POST':
        form = StatistikForm(request.POST)
        if form.is_valid():
            # Verarbeiten Sie die Daten je nach ausgewählter Statistik
            statistik_typ = form.cleaned_data['statistik_typ']
            start = form.cleaned_data['startdatum']
            end = form.cleaned_data['enddatum']
            location = form.cleaned_data['location']
            restaurant = form.cleaned_data['restaurant']
            segment = form.cleaned_data['segment']
            print("-------"+ statistik_typ + "---------") #Nur Debug
            if(statistik_typ == 'res_tag'):
                generateReservationGraph(start=start,end=end,location=location,givenRestaurant=restaurant, givenSegment=segment)
            if(statistik_typ == 'res_timeslot'):
                generateTimeslotGraph(start=start,end=end,location=location,givenRestaurant=restaurant, givenSegment=segment)
            if(statistik_typ == 'feedback'):
                generateFeedbackPlot(givenRestaurant=restaurant,isCustom=True,givenSegment=segment)
            # Logik für die Datenverarbeitung je nach statistik_typ
            return render(request, 'marketing/custom_input.html', {'form': form,'image':True})
    else:
        form = StatistikForm()
        print(form.fields)
        print("kl")
    return render(request, 'marketing/custom_input.html', {'form': form,'image':False})

def index_view(request):
    return redirect('customer_data_view')