from django.db import models


# Create your models here.

class Label(models.Model):
    productName = models.CharField(max_length=255, verbose_name="Desc")
    productCode = models.CharField(max_length=255, verbose_name="Part Number")
    productCode = models.CharField(max_length=255, verbose_name="Part Number")
    poNumber = models.CharField(max_length=255, verbose_name="PO")
    unit = models.DateField(verbose_name="Dispatch Date")
    qty = models.CharField(max_length=255)


class Barcode(models.Model):
    value = models.CharField(max_length=255)
class CustomLabel(models.Model):
    labelName = models.CharField(max_length=50, verbose_name="Desc")