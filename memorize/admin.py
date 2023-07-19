from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(FavouriteList)
admin.site.register(Word)
admin.site.register(Phrase)