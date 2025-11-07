from django.contrib import admin
from .models import Dog

@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = (
        "name", "breed", "age", "location",
        "microchip_number",           # ← NEW
        "activity_level", "training_difficulty",
        "coat_grooming", "weight_kg", "height_cm",
        "adopted",
    )
    list_filter = (
        "adopted", "activity_level", "training_difficulty",
        "coat_grooming", "location", "breed",
    )
    search_fields = ("name", "breed", "location", "description", "microchip_number")  # ← NEW
    ordering = ("name",)

