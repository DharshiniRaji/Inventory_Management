from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    
    brand = models.CharField(max_length=255, null=True, blank=True) 
    code = models.CharField(max_length=50, unique=True, null = True)  # Unique item code
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Price field
    size = models.CharField(max_length=50, null=True)  # Size field
    type = models.CharField(max_length=50, null=True)  # Type field
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)  # Foreign key to Category
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True) # User

    def __str__(self):
        return f"{self.brand} - {self.category.name}"  # Updated __str__ method
    

class Bill_details(models.Model):
    bill_number = models.CharField(max_length=10, unique=True)
    buyer_name = models.CharField(max_length=255)
    buyer_location = models.CharField(max_length=255)
    date_of_purchase = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    without_gst = models.BooleanField(default=False)

    def _str_(self):
        return self.bill_number

class Items_details(models.Model):
    bill = models.ForeignKey(Bill_details, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def total_price(self):
        return self.price * self.quantity