from .models import *
from django import forms
import datetime
from django.core.exceptions import ValidationError
#Forms:
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email','password','first_name','last_name')

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=Feedback
        fields=('vote','feedback')

class PromotionForm(forms.ModelForm):
    class Meta:
        model=Promotion
        fields=('title', 'description', 'start_date', 'end_date', 'discount_rate', 'loyality')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_discount_rate(self):
        discount_rate = self.cleaned_data.get('discount_rate')

        #Wird noch nicht benutzt, würde Prozentzeichen bereinigen
        if isinstance(discount_rate, str) and discount_rate.endswith('%'):
            try:
                percentage_value = float(discount_rate.replace('%', ''))
                discount_rate = percentage_value / 100.0
            except ValueError:
                raise ValidationError('Bitte geben Sie einen gültigen Rabattsatz ein.')


        #Wieder benutzter Code, der sicherstellt, dass der Wert zwischen 0 und 1 liegt (da es sich eigentlich um Prozente handelt!)
        if discount_rate < 0 or discount_rate >= 1:
            raise ValidationError('Der Rabattsatz muss zwischen 0 und 1 liegen.')

        return discount_rate

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number','role')

class ReservationForm(forms.ModelForm):
    date = forms.DateField(required=True, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(required=True, widget=forms.widgets.TimeInput(attrs={'type': 'time'}))
    class Meta:
        model = Reservation
        fields = ['date', 'time', 'party_size', 'special_requests']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        # Verbinden der Datum- und Zeit-Informationen in ein datetime Objekt
        if date and time:
            cleaned_data['date_time'] = datetime.datetime.combine(date, time)

        return cleaned_data

    def save(self, commit=True):
        # Entfernen Sie 'date' und 'time' aus cleaned_data, da diese nicht im Modell existieren
        cleaned_data = self.cleaned_data
        date_time = cleaned_data.pop('date_time', None)

        # Überschreiben des date_time Feldes des Modells mit dem kombinierten Wert
        instance = super(ReservationForm, self).save(commit=False)
        if date_time:
            instance.date_time = date_time
        if commit:
            instance.save()
        return instance
    
class DiningPreferenceForm(forms.Form):
    preferences = forms.ModelMultipleChoiceField(
        queryset=DiningPreference.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )