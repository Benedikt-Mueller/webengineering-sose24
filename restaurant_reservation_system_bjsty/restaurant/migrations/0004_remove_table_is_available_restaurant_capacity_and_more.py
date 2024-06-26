# Generated by Django 5.0.4 on 2024-06-05 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_promotion_loyality'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='table',
            name='is_available',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='capacity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='table',
            name='is_reserved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='cuisine',
            field=models.CharField(choices=[('international', 'Internationale Küche'), ('german', 'Deutsche Küche'), ('danish', 'Dänische Küche'), ('italian', 'Italienische Küche'), ('american', 'Amerikanische Küche'), ('indian', 'Indische Küche'), ('asian', 'Asiatische Küche')], max_length=50),
        ),
    ]
