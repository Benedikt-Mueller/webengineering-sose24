from restaurant.models import UserProfile,Restaurant,Reservation,DiningPreference,Feedback
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
    altersgruppen = pd.cut(df['age'], bins=[-1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], labels=['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100'])

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

def generateReservationGraph(location = None, start = None, end = None, givenRestaurant = None, givenSegment=None):
    isCustom = False
    if(start is not None):
        start_datum = datetime.datetime.combine(start, datetime.time())
        isCustom = True
    else:
        #Standardwert: 6 Wochen
        start_datum = datetime.datetime.today() - datetime.timedelta(weeks=6)

    if(end is not None):
        end_datum = datetime.datetime.combine(end, datetime.time())
        isCustom = True
    else:
        end_datum = datetime.datetime.today()
    
        

    # Erstellung einer Datumsreihe von start_datum bis end_datum
    datumsreihe = pd.date_range(start=start_datum, end=end_datum).date
    volle_datumsreihe_df = pd.DataFrame(datumsreihe, columns=['date'])

    # Daten beschaffen. Ist eine location angegeben, wird diese ebenfalls gefiltert:
    if location is not None and location != "":
        reservierungen = Reservation.objects.filter(date_time__range = (start_datum,end_datum), restaurant__location=location).order_by('date_time')
        isCustom = True
    else:
        reservierungen = Reservation.objects.filter(date_time__range = (start_datum,end_datum)).order_by('date_time')

    if givenRestaurant is not None and givenRestaurant != "":
        reservierungen = reservierungen.filter(restaurant__name__icontains=givenRestaurant)
        isCustom = True
    if (givenSegment is not None) and (givenSegment != ""):
        segment = interpetSegment(givenSegment)
        isCustom = True
        try:
            reservierungen = reservierungen.filter(customer__age__gte = segment[0], customer__age__lte = segment[1])
        except:
            noData('images/marketing/feedback_plot.png',isCustom)
            return 
    # Erstellen Sie ein DataFrame mit den Daten
    graph = pd.DataFrame(list(reservierungen.values('date_time', 'customer', 'restaurant', 'party_size', 'special_requests', 'status')))
    vollstaendiger_df = None #Variable im lokalen Kontext bekanntmachen
    if graph.empty:
        noData('images/marketing/reservation_graph.png', isCustom)
        return
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
    title = 'Reservierungen der letzten 6 Wochen pro Tag'
    if(isCustom):
        d1 = start_datum.date()
        d2 = end_datum.date()
        title = 'Reservierungen vom ' + str(d1) + ' bis zum ' + str(d2)
        if location is not None and location != "":
            title = title + ' in ' + location
        if givenRestaurant is not None and givenRestaurant != "":
            title = title + ' bei ' + givenRestaurant
        if segment is not None:
            title = title + '\nim Alterssegment ' + str(segment[0]) + ' bis ' + str(segment[1])
    plt.title(title)
    plt.xticks(rotation=45)  # Drehen Sie die Datumsbeschriftungen für bessere Lesbarkeit

    # Zeigen Sie das Diagramm an
    plt.tight_layout()
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/reservation_graph.png')
    if(isCustom):
        plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/custom.png')

    checkFolderExisting(plot_path)
    plt.savefig(plot_path)
    plt.close()
    

    

def generateTimeslotGraph(location = None, start = None, end = None, givenRestaurant = None, givenSegment = None):

    isCustom = False
    if(start is not None):
        start_datum = datetime.datetime.combine(start, datetime.time())
        isCustom = True
    else:
        #Standardwert: 52 Wochen
        start_datum = datetime.datetime.today() - datetime.timedelta(weeks=52)

    if(end is not None):
        end_datum = datetime.datetime.combine(end, datetime.time())
        isCustom = True
    else:
        end_datum = datetime.datetime.today()

    #Relevante Werte bestimmen:
    queryset = Reservation.objects.all().values('date_time', 'party_size')
    if(isCustom):
        queryset = queryset.filter(date_time__range = (start_datum,end_datum)).order_by('date_time')
        if location is not None and location != "":
            queryset = queryset.filter(date_time__range = (start_datum,end_datum), restaurant__location=location).order_by('date_time')
        if givenRestaurant is not None and givenRestaurant != "":
            queryset = queryset.filter(restaurant__name__icontains=givenRestaurant)
    
    if (givenSegment is not None) and (givenSegment != ""):
        segment = interpetSegment(givenSegment)
        isCustom = True
        try:
            queryset = queryset.filter(customer__age__gte = segment[0], customer__age__lte = segment[1])
        except:
            noData('images/marketing/feedback_plot.png',isCustom)
            return 
            
    #Dataframe laden:
    timeslot_bookings = pd.DataFrame(list(queryset))
    if timeslot_bookings.empty:
        noData('images/marketing/timeslot_graph.png', isCustom)
        return
    
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

    title = 'Durchschnittliche Buchungsanzahlen nach Zeitfenster'
    if(isCustom):
            d1 = start_datum.date()
            d2 = end_datum.date()
            title = 'Buchungen pro Zeitfenster vom ' + str(d1) + ' bis zum ' + str(d2) +'\n'
            if location is not None and location != "":
                title = title + ' in ' + location
            if givenRestaurant is not None and givenRestaurant != "":
                title = title + ' bei ' + givenRestaurant
            if(segment is not None):
                title = title + '\nim Alterssegment von ' + str(segment[0]) + ' bis ' + str(segment[1])

    plt.title(title)
    plt.xticks(rotation=45)
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/timeslot_graph.png')
    if(isCustom):
            plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/custom.png')
    checkFolderExisting(plot_path)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

def generateSeasonGraph():
    # Import:
    queryset = Reservation.objects.all().values('date_time', 'party_size')
    reservation_data = pd.DataFrame(list(queryset))
    reservation_data['season'] = reservation_data['date_time'].dt.date.apply(get_season)

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
    plt.ylabel('Vorlieben')
    plt.title('Beliebteste Küchen')

    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/preference_plot.png')
    checkFolderExisting(plot_path)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    
def generateFeedbackPlot(givenRestaurant=None, isCustom=False, givenSegment = None):
    # Import:
    queryset = Feedback.objects.all()
    
    if givenRestaurant is not None and givenRestaurant != "":
        queryset = queryset.filter(restaurant__name=givenRestaurant)
        isCustom = True
    
    segment = interpetSegment(givenSegment)
    if(segment is not None): 
        isCustom = True
        try:
            queryset = queryset.filter(customer__age__gte = segment[0], customer__age__lte = segment[1])
        except:
            noData('images/marketing/feedback_plot.png',isCustom)
            return 
    #Für Verarbeitung vorbereiten und Häufigkeit zählen
    queryset = queryset.values('vote').annotate(count=Count('vote'))
    ratingFrame = pd.DataFrame(list(queryset))
    
    #Leeren DataFrame abfangen:
    if ratingFrame.empty:
        noData('images/marketing/feedback_plot.png',isCustom)
        return
    # Labels bestimmen und anpassen:
    rating_labels = [label for _, label in Choices.VOTE_CHOICES]
    rating_values = [value for value, _ in Choices.VOTE_CHOICES]
    ratingFrame.columns = ['rating', 'count']
    ratingFrame['rating_label'] = ratingFrame['rating'].apply(lambda x: dict(Choices.VOTE_CHOICES)[x])

    # Merge-DataFrame:
    dummyFrame = pd.DataFrame({'rating': rating_values, 'rating_label': rating_labels})
    ratingFrameComplete = pd.merge(dummyFrame, ratingFrame, on='rating_label', how='left').fillna(0)
    ratingFrameComplete = ratingFrameComplete.sort_values(by='rating_label', ascending=True)

    # Seaborn Plot:
    plt.figure(figsize=(10, 6))
    sns.barplot(x='rating_label', y='count', data=ratingFrameComplete)
    plt.xlabel('Bewertung')
    plt.ylabel('Häufigkeit')
    title = 'Feedback nach Bewertung'
    plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/feedback_plot.png')
    if isCustom:
        if (givenRestaurant is not None) and (givenRestaurant != ""):
            title = title + ' bei ' + givenRestaurant
        if segment is not None:
            title = title + '\nin der Altersspanne ' + str(segment[0]) + " - " + str(segment[1])
        plot_path = os.path.join(settings.MEDIA_ROOT, 'images/marketing/custom.png')
    plt.title(title)
    checkFolderExisting(plot_path)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

#-----------------------------------------------------------------------------------------------------#
#Interne Methoden:
#-----------------------------------------------------------------------------------------------------#
def interpetSegment(givenSegment):
    if givenSegment is not None and givenSegment != "":
        givenSegment.replace(" ","")
        ageList = givenSegment.split('-')
        if len(ageList) < 2:
            ageList.append(ageList[0])
        return ageList
    else:
        return None

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

def noData(path, isCustom=False):
    origin = os.path.join(settings.MEDIA_ROOT,'images/marketing/no_data.png')
    if isCustom:
        path = 'images/marketing/custom.png'
    destination = os.path.join(settings.MEDIA_ROOT,path)
    shutil.copy2(origin, destination)