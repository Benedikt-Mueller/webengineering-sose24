from restaurant.models import UserProfile,Restaurant,Reservation,DiningPreference
from restaurant.choices import Choices
from django.db.models import Count
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') #Ändert das Backend auf ein nicht gui-basiertes Backend. Nimmt man diese Zeile raus, stürzt der Server bei jedem Reload ab!
import pandas as pd
import seaborn as sns
import os
import shutil
from django.conf import settings
import datetime
from django.utils.timezone import make_aware


#-----------------------------------------------------------------------------------------------------#
#Methoden zur Statistikgeneration:
#-----------------------------------------------------------------------------------------------------#

def generateAgePlot():
    # Import:
    query_set = UserProfile.objects.all().values('age')
    df = pd.DataFrame(list(query_set))

    # Gruppen erstellen:
    altersgruppen = pd.cut(df['age'], bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], labels=['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100'])

    # Plot erzeugen
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(x=altersgruppen)
    ax.set_title('Verteilung des Alters')
    ax.set_xlabel('Altersgruppen')
    ax.set_ylabel('Anzahl der Benutzer')

    # Plot speichern (Datei wird im Backend statisch aufgerufen:)
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/altersgruppen_plot.png')
    checkFolderExisting(plot_path)
    plt.savefig(plot_path)
    plt.tight_layout()
    plt.close()

def generateReservationGraph(weeks_old = 6, location = None):

    start_datum = datetime.datetime.today() - datetime.timedelta(weeks=weeks_old)
    end_datum = datetime.datetime.today()

    # Erstellung einer Datumsreihe von start_datum bis end_datum
    datumsreihe = pd.date_range(start=start_datum, end=end_datum).date
    volle_datumsreihe_df = pd.DataFrame(datumsreihe, columns=['date'])

    # Berechnen Sie das Datum vor 6 Wochen
    time_ago = make_aware(datetime.datetime.today() - datetime.timedelta(weeks=6))

    # Daten beschaffen. Ist eine location angegeben, wird diese ebenfalls gefiltert:
    if location is not None:
        reservierungen = Reservation.objects.filter(date_time__gte=time_ago, restaurant__location=location).order_by('date_time')
    else:
        reservierungen = Reservation.objects.filter(date_time__gte=time_ago).order_by('date_time')

    # Erstellen Sie ein DataFrame mit den Daten
    graph = pd.DataFrame(list(reservierungen.values('date_time', 'customer', 'restaurant', 'party_size', 'special_requests', 'status')))
    vollstaendiger_df = None #Variable im lokalen Kontext bekanntmachen
    if not graph.empty:
        print("Der Graf")
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

    #Existieren keine Daten, wird das "no data availabe"-PNG statt der Statistik angezeigt.
    else:
        print("No data")
        origin = os.path.join(settings.MEDIA_ROOT,'images/marketing/no_data.png')
        print(settings.MEDIA_ROOT)
        print(origin)
        destination = os.path.join(settings.MEDIA_ROOT,'images/marketing/reservation_graph.png')
        shutil.copy2(origin, destination)
    

    

def generateTimeslotGraph():
    #Dataframe laden:
    queryset = Reservation.objects.all().values('date_time', 'party_size')
    timeslot_bookings = pd.DataFrame(list(queryset))
    timeslot_bookings['time_slot'] = timeslot_bookings['date_time'].apply(get_time_slot)
    average_bookings = timeslot_bookings.groupby('time_slot')['party_size'].mean().reset_index()
    average_bookings = average_bookings[average_bookings['time_slot'] != 'no_category']
    #Zweiten Dataframe laden, damit auch leere Uhrzeiten angezeigt werden:
    all_time_slots = pd.DataFrame({
    'time_slot': ['06-10 Uhr','10-12 Uhr', '13-15 Uhr', '16-17 Uhr', '18-19 Uhr', '20-22 Uhr','23-06 Uhr']
    })
    #Beide Dfs verbinden:
    average_bookings_complete = pd.merge(
    all_time_slots,
    average_bookings,
    on='time_slot',
    how='left'
    )
    #0 (Zahl) statt NaN einfügen:
    average_bookings_complete['party_size'] = average_bookings_complete['party_size'].fillna(0)

    # Seaborn / Matplotlib:
    sns.barplot(x='time_slot', y='party_size', data=average_bookings_complete)
    plt.xlabel('Zeitfenster')
    plt.ylabel('Durchschnittliche Buchungsanzahl')
    plt.title('Durchschnittliche Buchungsanzahlen nach Zeitfenster')
    plt.xticks(rotation=45)
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/timeslot_graph.png')
    checkFolderExisting(plot_path)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

def generateSeasonGraph():
    # Import:
    queryset = Reservation.objects.all().values('date_time', 'party_size')
    print(queryset)
    reservation_data = pd.DataFrame(list(queryset))
    print(reservation_data)
    reservation_data['season'] = reservation_data['date_time'].dt.date.apply(get_season)
    print(reservation_data)

    # Durchschnitt berechnen:
    average_bookings_by_season = reservation_data.groupby('season')['party_size'].mean().reset_index()

    # Seaborn / Matplotlib:
    sns.barplot(x='season', y='party_size', data=average_bookings_by_season, order=['Winter', 'Frühling', 'Sommer', 'Herbst'])
    plt.xlabel('Saison')
    plt.ylabel('Durchschnittliche Reservierungen')
    plt.title('Durchschnittliche Reservierungen nach Saison')
    plt.xticks(rotation=45)
    
    #Speichern:
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/season_graph.png')
    checkFolderExisting(plot_path)  # Funktion, um zu überprüfen/erstellen des Verzeichnisses
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

def generateDiningPreferencePlot():
    # Labels bestimmen:
    preference_labels = [label for _, label in Choices.PREFERENCE_CHOICES]
    preference_values = [value for value, _ in Choices.PREFERENCE_CHOICES]

    # Import:
    queryset = DiningPreference.objects.values('preferences').annotate(count=Count('preferences'))
    preferenceFrame = pd.DataFrame(list(queryset))

    # Labels anpassen:
    preferenceFrame.columns = ['preference', 'count']

    # Umwandeln von preferences in lesbare Labels
    preferenceFrame['preference_label'] = preferenceFrame['preference'].apply(lambda x: dict(Choices.PREFERENCE_CHOICES)[x])

    # Merge-Dataframe:
    dummyframe = pd.DataFrame({'preference': preference_values, 'preference_label': preference_labels})
    preferenceFrameComplete = pd.merge(dummyframe, preferenceFrame, on='preference_label', how='left').fillna(0)
    preferenceFrameComplete = preferenceFrameComplete.sort_values(by='count', ascending=False)

    # Seaborn:
    plt.figure(figsize=(10, 6))
    sns.barplot(x='count', y='preference_label', data=preferenceFrameComplete)
    plt.xlabel('Häufigkeit')
    plt.ylabel('Dining Preference')
    plt.title('Häufigkeit der Dining Preferences')

    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/preference_plot.png')
    checkFolderExisting(plot_path)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

#-----------------------------------------------------------------------------------------------------#
#Interne Methoden:
#-----------------------------------------------------------------------------------------------------#

def checkFolderExisting(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

#Ausgelagerte Methode zum Berechnen der Timeslots in generateTimeslotGraph()
def get_time_slot(date_time):
    time = date_time.time()
    if datetime.time(6, 0) <= time < datetime.time(10, 0):
        return '06-10 Uhr'
    elif datetime.time(10, 0) <= time < datetime.time(13, 0):
        return '10-12 Uhr'
    elif datetime.time(13, 0) <= time < datetime.time(16, 0):
        return '13-15 Uhr'
    elif datetime.time(16, 0) <= time < datetime.time(18, 0):
        return '16-17 Uhr'
    elif datetime.time(18, 0) <= time < datetime.time(20, 0):
        return '18-19 Uhr'
    elif datetime.time(20, 0) <= time < datetime.time(23, 0):
        return '20-22 Uhr'
    else:
        return '23-06 Uhr'
    
def get_season(date):
    year = date.year
    if not isinstance(date, pd.Timestamp):
        date = pd.Timestamp(date)
        print("Großes Erfolg!")
    #Schaltjahre:
    feb_end = '02-29' if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else '02-28'
    seasons = {
        'Winter': pd.date_range(start=f"{year}-12-01", end=f"{year}-12-31").union(
                  pd.date_range(start=f"{year}-01-01", end=f"{year}-{feb_end}")),
        'Frühling': pd.date_range(start=f"{year}-03-01", end=f"{year}-05-31"),
        'Sommer': pd.date_range(start=f"{year}-06-01", end=f"{year}-08-31"),
        'Herbst': pd.date_range(start=f"{year}-09-01", end=f"{year}-11-30")
    }
    for season, date_range in seasons.items():
        if date in date_range:
            return season
    return 'Unbekannt'  # Für den Fall, dass das Datum nicht zugeordnet werden kann (Schaltjahr beachten)