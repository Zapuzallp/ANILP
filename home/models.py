from django.db import models

# Create your models here.

class Label(models.Model):
    productName = models.CharField(max_length=255)
    productCode = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    qty = models.CharField(max_length=255)

class Barcode(models.Model):
    value = models.CharField(max_length=255)