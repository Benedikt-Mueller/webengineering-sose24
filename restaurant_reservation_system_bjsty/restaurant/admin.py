from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(Table)