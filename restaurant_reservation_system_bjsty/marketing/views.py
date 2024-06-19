from django.shortcuts import render
from restaurant.models import UserProfile,Restaurant,Reservation
from django.http import HttpResponse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

# Create your views here.
def customer_data_view(request):
    # Daten aus dem UserProfile Modell in einen DataFrame extrahieren
    query_set = UserProfile.objects.all().values('age')
    df = pd.DataFrame(list(query_set))

    # Alter in Gruppen einteilen
    altersgruppen = pd.cut(df['age'], bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], labels=['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100'])

    # Plot vorbereiten
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(x=altersgruppen)
    ax.set_title('Verteilung des Alters')
    ax.set_xlabel('Altersgruppen')
    ax.set_ylabel('Anzahl der Benutzer')

    # Plot als Bild speichern
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/altersgruppen_plot.png')
    checkFolderExisting(plot_path)
    plt.savefig(plot_path)
    plt.close()
    generateReservationGraph()
    #Website anzeigen:
    return render(request, 'marketing/customer_data.html')

def checkFolderExisting(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def generateReservationGraph():

    start_datum = datetime.today() - timedelta(weeks=6)
    end_datum = datetime.today()

    # Erstellung einer Datumsreihe von start_datum bis end_datum
    datumsreihe = pd.date_range(start=start_datum, end=end_datum).date
    volle_datumsreihe_df = pd.DataFrame(datumsreihe, columns=['date'])

    # Berechnen Sie das Datum vor 6 Wochen
    time_ago = make_aware(datetime.today() - timedelta(weeks=6))

    # Query, um alle Reservierungen der letzten 6 Wochen zu holen
    reservierungen = Reservation.objects.filter(date_time__gte=time_ago).order_by('date_time')

    # Erstellen Sie ein DataFrame mit den Daten
    graph = pd.DataFrame(list(reservierungen.values('date_time', 'customer', 'restaurant', 'party_size', 'special_requests', 'status')))
    # Konvertieren Sie `date_time` zu nur einem Datum (ohne Zeit)
    graph['date'] = graph['date_time'].dt.date

    # Gruppieren Sie die Daten nach dem Datum und zählen Sie die Anzahl der Reservierungen pro Tag
    reservierungen_pro_tag = graph.groupby('date').size()
    # Reset index, um das Datum als separate Spalte zu haben
    reservierungen_pro_tag = reservierungen_pro_tag.reset_index(name='Anzahl der Reservierungen')

    vollstaendiger_df = pd.merge(volle_datumsreihe_df, reservierungen_pro_tag, on='date', how='left').fillna(0)
    vollstaendiger_df['Anzahl der Reservierungen'] = vollstaendiger_df['Anzahl der Reservierungen'].astype(int)

    # Erstellen Sie ein Liniendiagramm
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='date', y='Anzahl der Reservierungen', data=vollstaendiger_df)

    # Setzen Sie die Beschriftungen und Titel
    plt.xlabel('Datum')
    plt.ylabel('Anzahl der Reservierungen')
    plt.title('Reservierungen der letzten 6 Wochen pro Tag')
    plt.xticks(rotation=45)  # Drehen Sie die Datumsbeschriftungen für bessere Lesbarkeit

    # Zeigen Sie das Diagramm an
    plt.tight_layout()
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/reservation_graph.png')
    checkFolderExisting(plot_path)
    plt.savefig(plot_path)
    plt.close()
