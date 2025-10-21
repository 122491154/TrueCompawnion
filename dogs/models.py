from django.db import models

class Dog(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='dogs/', blank=True, null=True)
    adopted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
