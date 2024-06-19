from django.shortcuts import render
from restaurant.models import UserProfile,Restaurant
from django.http import HttpResponse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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
    plot_path = 'static/images/marketing/altersgruppen_plot.png'
    plt.savefig(plot_path)
    plt.close()

    # Bildpfad an das Template senden
    context = {'plot_path': plot_path}
    return render(request, 'customer_data.html', context)