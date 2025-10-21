from django.contrib import admin
from .models import Dog

@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'age', 'location', 'adopted')
    search_fields = ('name', 'breed', 'location')
    list_filter = ('adopted', 'breed')
