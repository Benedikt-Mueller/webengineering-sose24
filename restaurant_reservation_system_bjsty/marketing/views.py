from django.shortcuts import render
from .functions import * #Erlaub Zugriff auf die ausgelagerten Funktionen

#Die Statistiken dieses Marketing-Moduls verwenden Matplotlib, Pandas und Seaborn, da wir diese Module auch im Kurs "Data Science" verwenden und damit vertraut sind. Außerdem können Performanceprobleme auf Clientseite so ausgeschlossen werden,
#die bei JavaScript gegebenenfalls auftreten können. Die Statistiken werden über ausgelagerte Methoden als Bild generiert und anschließend im Template geladen. 

# Create your views here.
def customer_data_view(request):
    

    #Statistiken erstellen (bei Performanceproblemen sollte man diesen Schritt zeitgestuert als Cronjob [oder Windows-Equivalent] ausführen, aber dann können Daten veraltet sein):
    generateAgePlot()
    generateReservationGraph()
    generateTimeslotGraph()
    generateDiningPreferencePlot()
    generateSeasonGraph()
    #Template anzeigen:++
    return render(request, 'marketing/customer_data.html')