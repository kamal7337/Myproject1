from django.db import models


class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    Batch = models.IntegerField(null=False)
    weight = models.IntegerField(null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.name} ({self.role})"