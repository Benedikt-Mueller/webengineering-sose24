from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import *
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserForm, ProfileForm
from django.views.decorators.http import require_POST
from django.urls import reverse
from .forms import *
from django.forms import modelformset_factory
from django.utils import timezone
from django.core.mail import send_mail
from zoneinfo import ZoneInfo
from django.shortcuts import render
from .models import Table
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def table_list(request):
    tables = Table.objects.all()
    remaining_tables = Table.objects.filter(is_reserved=False)

    context = {
        'restaurant_name': 'Pasha\'s Palace',  # Beispiel für den Restaurantnamen
        'tables': tables,
        'remaining_tables': remaining_tables,
    }
    return render(request, 'restaurant/table_list.html', context)


# views:
def index(request):
    return redirect(restaurant_list)

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
            return redirect('login_view')  # Angenommen, es existiert eine Login-Seite.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'restaurant/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

"""
def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurant/restaurant_list.html', {'restaurants': restaurants})
  """
def restaurant_list(request):
    form = SearchForm(request.GET or None)
    restaurants = Restaurant.objects.all()

    if form.is_valid():
        if form.cleaned_data['location']:
            restaurants = restaurants.filter(location__icontains=form.cleaned_data['location'])
        if form.cleaned_data['cuisine']:
            restaurants = restaurants.filter(cuisine__icontains=form.cleaned_data['cuisine'])
        if form.cleaned_data['capacity']:
            restaurants = restaurants.filter(capacity__gte=form.cleaned_data['capacity'])

    return render(request, 'restaurant/restaurant_list.html', {
        'restaurants': restaurants,
        'form': form
    })

def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_items = Menu.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/menu.html', {'restaurant': restaurant, 'menu_items': menu_items})

def view_tables(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/tables.html', {'restaurant': restaurant, 'tables': tables})

@login_required
def create_reservation(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.restaurant = restaurant
            reservation.customer = request.user.userprofile  # Vorausgesetzt der User ist eingeloggt
            reservation.status = 'pending'
            reservation.save()
            return redirect('restaurant_list')  # Angenommen, Sie haben eine URL für Reservierungserfolg
    else:
        form = ReservationForm()
    return render(request, 'restaurant/create_reservation.html', {'form': form, 'restaurant': restaurant})

@login_required
def startpage_view(request):
    userprofile = get_object_or_404(UserProfile, user = request.user)
    if userprofile.role == "owner":
            return redirect('owner_view')
    elif userprofile.role == "developer":
            return redirect(reverse('admin:index'))
    else:
        diningPreferences = DiningPreference.objects.filter(customer=userprofile)
        return render(request, 'restaurant/profile_view.html', {'user':request.user, 'userprofile':userprofile,'preferences':diningPreferences })

@login_required
def profile_view(request):
    userprofile = get_object_or_404(UserProfile, user = request.user)
    diningPreferences = DiningPreference.objects.filter(customer=userprofile)
    return render(request, 'restaurant/profile_view.html', {'user':request.user, 'userprofile':userprofile,'preferences':diningPreferences })

@login_required
def create_feedback(request, restaurant_id):
    userprofile = get_object_or_404(UserProfile, user = request.user)
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.restaurant=restaurant
            feedback.customer=userprofile
            feedback.save()
            return redirect('restaurant_list')
    else:
        form = FeedbackForm
        return render(request, 'restaurant/create_feedback.html', {'form': form, 'restaurant': restaurant})    
def view_feedback(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    feedbacks = Feedback.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/view_feedback.html',({'feedbacks':feedbacks, 'restaurant':restaurant}))

def create_promotion(request,restaurant_id):
    restaurant = get_object_or_404(Restaurant,pk=restaurant_id)
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.restaurant=restaurant
            promotion.save()
            return redirect('restaurant_list')
        else:
            return render(request, 'restaurant/create_promotion.html', {
                'form': form,
                'restaurant': restaurant
            })
    else:
        form = PromotionForm
        return render(request, 'restaurant/create_promotion.html', {'form': form, 'restaurant': restaurant}) 
    
@login_required
def dining_preference(request):
       user_profile = UserProfile.objects.get(user=request.user)

       if request.method == 'POST':
           form = DiningPreferenceForm(request.POST)
           if form.is_valid():
               selected_preferences = form.cleaned_data['preferences']
               # Lösche alle bestehenden Präferenzen, um sie durch die neuen Auswahlmöglichkeiten zu ersetzen.
               user_profile.diningpreference_set.clear()
               for preference in selected_preferences:
                   DiningPreference.objects.create(customer=user_profile, preferences=preference.preferences)
               return redirect('success_url')  # URL nach Erfolg anpassen
       else:
           form = DiningPreferenceForm()
           # Optional: Vorauswahlen basierend auf existierenden Präferenzen des Benutzers
           form.fields['preferences'].initial = user_profile.diningpreference_set.all()

       return render(request, 'restaurant/manage_preferences.html', {'form': form})

# ---- Reservations: ---- #
def auto_assign_tables(reservations, tables, request_date):
    reservations = reservations.order_by('party_size')
    tables = tables.order_by('capacity')
    isPossible = False
    for reservation in reservations:
        for table in tables:
            if table.capacity >= reservation.party_size:
                reservation_table_link = ReservationTableLink(
                        reservation=reservation,
                        table=table,
                        date=request_date
                    )
                reservation_table_link.save()
                reservation.status = 'confirmed'
                reservation.save()
                isPossible = True
                break
        if isPossible == False:
            reservation.status = "cancelled"
            reservation.save()
        isPossible = False
    
    
        

@login_required
def manage_reservations(request, restaurant_id, date=None):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if(date == None):
        request_date =  timezone.now().date()
    else:
        request_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    reservations = Reservation.objects.filter(restaurant=restaurant, date_time__date=request_date,status = 'pending')
    tables = Table.objects.filter(restaurant=restaurant)
    for table in tables:
        blockedTableLink = ReservationTableLink.objects.filter(table=table, date=request_date).first()
        if blockedTableLink:
            blockedTable = blockedTableLink.table
            pk = blockedTable.pk
            tables = tables.exclude(pk = pk)
            print(tables)

    if request.method == 'POST':
        if 'auto_assign' in request.POST:
            auto_assign_tables(reservations, tables, request_date)
            return redirect('owner_view')
        if 'dateButton' in request.POST:
            postDate = request.POST.get('dateInput',None)
            if (postDate is None) or (postDate == ""):
                return redirect('manage_reservations', restaurant_id=restaurant_id)
            else:
                return redirect(reverse('manage_reservations_by_date',args=(restaurant_id,postDate)))
        else:
            for key, value in request.POST.items():
                if key.startswith('table-'):
                    reservation_id = int(key.split('-')[1])
                    table_id = int(value)
                    table = get_object_or_404(Table,pk=table_id)
                    reservation = get_object_or_404(Reservation, pk=reservation_id)
                    reservation.status = 'confirmed'
                    reservation_table_link = ReservationTableLink(
                        reservation=reservation,
                        table=table,
                        date=request_date
                    )
                    print('----------------------')
                    print(reservation)
                    print(table)
                    print(reservation)
                    if table.capacity >= reservation.party_size:
                        reservation_table_link.save()
                        reservation.save()
                    else:
                        reservation.status = 'cancelled'
                        reservation.save()
                    
            return redirect('owner_view')

    else:
        return render(request, 'restaurant/manage_reservations.html', {
        'restaurant': restaurant,
        'reservations': reservations,
        'tables': tables,
        'selected_date': request_date
        })

def search_restaurants(request):
    form = SearchForm(request.GET or None)
    results = None
    if form.is_valid():
        results = Restaurant.objects.all()
        if form.cleaned_data['location']:
            results = results.filter(location__icontains=form.cleaned_data['location'])
        if form.cleaned_data['cuisine']:
            results = results.filter(cuisine__icontains=form.cleaned_data['cuisine'])
        if form.cleaned_data['capacity']:
            results = results.filter(capacity__gte=form.cleaned_data['capacity'])
    return render(request, 'restaurant/search.html', {'form': form, 'results': results})

# Tisch Freigabe
@login_required  # Sicherstellen, dass nur eingeloggte Benutzer Zugriff haben
def release_table(request, table_id):
    # Holt den Tisch oder zeigt eine 404-Seite, falls nicht gefunden
    table = get_object_or_404(Table, id=table_id)
    
    if request.method == 'POST':
        # Setzt den Tisch auf nicht reserviert und speichert die Änderung
        table.is_reserved = False
        table.save()
        return redirect('tables_list')  # Leitet den Benutzer auf die Übersichtsseite der Tische um
    
    # Zeigt das Bestätigungsformular zum Freigeben des Tisches an
    return render(request, 'restaurant/release_table.html', {'table': table})

# Reservierung Anpassen und E-Mails an Kunden und Bestzern senden
@login_required
def adjust_reservation(request, reservation_id):
    currentCustomer = get_object_or_404(UserProfile, user=request.user)
    reservation = get_object_or_404(Reservation, id=reservation_id, customer=currentCustomer)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            temp_reservation = form.save(commit=False)
            # Setzt den Status auf "Pending"
            temp_reservation.status = 'pending'  
            link = ReservationTableLink.objects.filter(reservation=temp_reservation).first()
            link.delete()
            temp_reservation.save()
            send_confirmation_email(reservation)
            return redirect('view_reservation', reservation_id=reservation.id)
    else:
        # Ausgeben der Form, als Standardwerte wird die Instanz, also die ausgewählt Reservierung, angegeben. Die Werte müssen allerdings seperat initialisiert werden, da im Model nur ein DateTime Field existiert, die Form aber seperate Felder hat
        initial_data = {
            'date': reservation.date_time.date(),
            'time': reservation.date_time.time(),
            'party_size': reservation.party_size,
            'special_requests': reservation.special_requests,
            # Füge weitere Felder hinzu, falls nötig
        }
        form = ReservationForm(instance=reservation,initial=initial_data)

    return render(request, 'restaurant/adjust_reservation.html', {'form': form})

def view_reservation(request,reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    initial_data = {
            'date': reservation.date_time.date(),
            'time': reservation.date_time.time(),
            'party_size': reservation.party_size,
            'special_requests': reservation.special_requests,
            # Füge weitere Felder hinzu, falls nötig
        }
    form = ReservationForm(instance=reservation,initial=initial_data)
    return render(request,"restaurant/view_reservation.html", {"form":form})

@login_required
def my_reservations(request):
    current_customer = get_object_or_404(UserProfile, user = request.user)
    reservations = Reservation.objects.filter(customer=current_customer).order_by('-date_time')  # Die neueste zuerst
    return render(request, 'restaurant/my_reservations.html', {'reservations': reservations})


def send_confirmation_email(reservation):
    subject = 'Ihre Reservierung wurde angepasst'
    message = f'Liebe(r) {reservation.customer.user.email}, Ihre Reservierung für den {reservation.date_time.strftime("%Y-%m-%d %H:%M")} wurde erfolgreich angepasst.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [reservation.customer.user.email, settings.OWNER_EMAIL]
    #Die folgende Zeile muss auskommentiert werden, damit auch tatsächlich eine Mail gesendet wird. Dafür brauchen wir aber einen entsprechenden Provider (Mailserver hätte ich, Konfiguration hat aber erstmal keine Priorität)
    send_mail(subject, message, email_from, recipient_list)

@login_required
def change_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner__user=request.user)
    # Erstellt ein Formset für Restaurantbilder
    ImageFormSet = modelformset_factory(RestaurantImage, form=RestaurantImageForm, extra=3)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            # Weiterleitung, z.B. zurück zur Restaurantübersicht
            return redirect('restaurant_list')
    else:
        form = RestaurantForm(instance=restaurant)
        formset = ImageFormSet(queryset=RestaurantImage.objects.filter(restaurant=restaurant))
    return render(request, 'restaurant/change_restaurant.html', {'form': form, 'formset': formset, 'restaurant' : restaurant})
#Bilder löschen:
@login_required
def delete_image(request, image_id):
    image = get_object_or_404(RestaurantImage, id=image_id, restaurant__owner__user=request.user)
    primary = image.restaurant.pk
    url = "/restaurant/restaurant/{}/change_restaurant".format(primary)
    if request.method == 'POST':
        image.delete()
        return redirect(url)  # URL zum Bearbeiten des Restaurants
    else:
        # Hinweis anzeigen oder Bestätigungsseite für das Löschen rendern
        return render(request, 'restaurant/confirm_delete.html', {'object': image})
#Bilder hochladen:   
@require_POST
@login_required
def upload_images(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    images = request.FILES.getlist('images')
    for image in images:
        RestaurantImage.objects.create(restaurant=restaurant, image=image)

    return JsonResponse({'message': 'Bilder wurden erfolgreich hochgeladen!'})

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    images = restaurant.images.all()
    feedbacks = Feedback.objects.filter(restaurant=restaurant)
    menu_items = Menu.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/restaurant_detail.html', {'restaurant': restaurant, 'images': images,'feedbacks':feedbacks,'menu_items':menu_items})

#Register
def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('profile')  # or any other page
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Weiterleitung zur Startseite oder einer anderen Seite
                next_page = request.POST.get('next', 'restaurant_list')
                get_page = request.GET.get('next', 'restaurant_list')
                if(get_page != 'restaurant_list'): next_page = get_page
                return redirect(next_page)
            else:
                messages.error(request, 'Ungültige Anmeldedaten.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def owner_view(request):
    currentUser = get_object_or_404(UserProfile, user=request.user)
    print(str(currentUser.role))
    if(currentUser.role != 'owner' and currentUser.role != 'developer' and currentUser.role != 'admin'):
        return redirect('staff_view')
    restaurants = Restaurant.objects.filter(owner=currentUser)
    return render(request, 'restaurant/owner_view.html', {'restaurants':restaurants})

@login_required
def staff_view(request):
    currentUser = get_object_or_404(UserProfile, user=request.user)
    restaurants = Restaurant.objects.filter(owner=currentUser)
    if(currentUser.role != 'owner' and currentUser.role != 'developer' and currentUser.role != 'staff' and currentUser.role != 'admin'):
         return HttpResponseForbidden("Zugriff verweigert: Sie verfügen nicht über die nötigt Berechtigung, um dieses System zu nutzen!") 
    return render(request, 'restaurant/staff_view.html', {'restaurants':restaurants})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sie wurden erfolgreich abgemeldet.')
    return redirect('restaurant_list')