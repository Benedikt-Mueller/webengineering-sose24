# Generated by Django 5.0.4 on 2024-05-29 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diningpreference',
            name='feedback',
        ),
        migrations.AlterField(
            model_name='diningpreference',
            name='preferences',
            field=models.CharField(choices=[('international', 'Internationale Küche'), ('german', 'Deutsche Küche'), ('danish', 'Dänische Küche'), ('italian', 'Italienische Küche'), ('american', 'Amerikanische Küche'), ('indian', 'Indische Küche'), ('asian', 'Asiatische Küche')], max_length=50),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.CharField(choices=[('one_star', '1/5'), ('two_star', '2/5'), ('three_star', '3/5'), ('four_star', '4/5'), ('five_star', '5/5')], max_length=10)),
                ('feedback', models.TextField(blank=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.userprofile')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.restaurant')),
            ],
        ),
    ]
