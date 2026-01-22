from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ClientProfile(models.Model):
    """Extra details for a logged-in client (DoneDeal-style profile)."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    county = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)

    # NEW: housing document PDF upload
    housing_document = models.FileField(
        upload_to="housing_docs/",
        blank=True,
        null=True,
        help_text="Upload your housing / tenancy document as a PDF.",
    )

    def __str__(self):
        return self.full_name or self.user.username


class Dog(models.Model):
    # NEW: Adoption status (available/reserved/adopted)
    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_RESERVED = "RESERVED"
    STATUS_ADOPTED = "ADOPTED"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_ADOPTED, "Adopted"),
    ]

    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="dogs/", blank=True, null=True)

    # KEEP your existing field so old templates/views don't break.
    # We'll keep it in sync with the new `status` field.
    adopted = models.BooleanField(default=False)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )

    microchip_number = models.CharField(
        max_length=50, blank=True, null=True, unique=True
    )

    ACTIVITY_LEVEL_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    activity_level = models.CharField(
        max_length=20,
        blank=True,
        choices=ACTIVITY_LEVEL_CHOICES,
    )

    COAT_GROOMING_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    coat_grooming = models.CharField(
        max_length=20,
        blank=True,
        choices=COAT_GROOMING_CHOICES,
    )

    TRAINING_DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Moderate", "Moderate"),
        ("Challenging", "Challenging"),
    ]
    training_difficulty = models.CharField(
        max_length=20,
        blank=True,
        choices=TRAINING_DIFFICULTY_CHOICES,
    )

    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        # Keep legacy boolean in sync
        self.adopted = self.status == self.STATUS_ADOPTED
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

class DogImage(models.Model):
    dog = models.ForeignKey(
        Dog,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="dogs/multi/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dog.name} image {self.id}"

class AdoptionRequest(models.Model):
    """A user's request to adopt a specific dog."""

    STATUS_PENDING = "PENDING"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    dog = models.ForeignKey(
        Dog,
        on_delete=models.CASCADE,
        related_name="adoption_requests",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="adoption_requests",
    )

    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_adoption_requests",
    )
    admin_note = models.TextField(blank=True)

    class Meta:
        unique_together = ("dog", "user")

    def mark(self, new_status: str, reviewed_by: User | None = None, admin_note: str = ""):
        self.status = new_status
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewed_by
        if admin_note:
            self.admin_note = admin_note
        self.save()

    def __str__(self) -> str:
        return f"{self.user.username} → {self.dog.name} ({self.status})"


class Notification(models.Model):
    """Simple in-app notification for a user."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=120)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=300, blank=True)  # store a URL path e.g. "/dogs/3/"
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username}: {self.title}"


class FavouriteDog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favourite_dogs",
    )
    dog = models.ForeignKey(
        Dog,
        on_delete=models.CASCADE,
        related_name="favourited_by",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "dog")

    def __str__(self) -> str:
        return f"{self.user.username} → {self.dog.name}"
