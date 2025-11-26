from django.db import models
class Student(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Company(models.Model):
    company_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

# Create your models here.
