
from django import forms

class StatistikForm(forms.Form):
    STATISTIK_AUSWAHL = [
        ('no_select', 'Wählen Sie eine Statistik'),
        ('res_tag', 'Reservierungen nach Tag'),
        ('res_timeslot', 'Reservierungen nach Timeslot'),
        ('feedback', 'Feedback'),
    ]
    statistik_typ = forms.ChoiceField(choices=STATISTIK_AUSWAHL, label='Statistik Typ', required=True)
    startdatum = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), label='Startdatum', required=True)
    enddatum = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), label='Enddatum', required=False)
    location = forms.CharField(max_length=100, label='Ort', required=False)
    restaurant = forms.CharField(max_length=100, label='Restaurant', required=False)