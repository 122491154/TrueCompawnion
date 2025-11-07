from django.db import models

class Dog(models.Model):
    # --- Core info ---
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='dogs/', blank=True, null=True)
    adopted = models.BooleanField(default=False)
    microchip_number = models.CharField(max_length=50, blank=True, null=True, unique=True)  # ✅ NEW FIELD

    # --- New filter fields ---
    ACTIVITY_LEVEL_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    activity_level = models.CharField(
        max_length=20, blank=True, choices=ACTIVITY_LEVEL_CHOICES
    )

    COAT_GROOMING_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    coat_grooming = models.CharField(
        max_length=20, blank=True, choices=COAT_GROOMING_CHOICES
    )

    TRAINING_DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Moderate", "Moderate"),
        ("Challenging", "Challenging"),
    ]
    training_difficulty = models.CharField(
        max_length=20, blank=True, choices=TRAINING_DIFFICULTY_CHOICES
    )

    # --- Size (weight + height) ---
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        return self.name

