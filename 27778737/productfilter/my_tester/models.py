from django.db import models


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField()
    description = models.TextField()
    release_date = models.DateField()


class Brand(models.Model):
    id = models.AutoField()
    name = models.CharField()
