from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, InventoryItem, Bill_details, Items_details



class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class InventoryItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InventoryItemForm, self).__init__(*args, **kwargs)
        
        # Define default categories
        default_categories = ["Men", "Women", "Children"]
        
        # Ensure these categories exist in the database
        for cat in default_categories:
            Category.objects.get_or_create(name=cat)  # Creates if not exists

        # Fetch all categories including defaults
        self.fields['category'].queryset = Category.objects.all()

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Avoid stale data before initialization
        empty_label="Select Category"  # Optional placeholder
    )

    class Meta:
        model = InventoryItem
        fields = ['brand', 'code', 'price', 'size', 'type', 'quantity', 'category']

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill_details
        fields = ['buyer_name', 'buyer_location', 'without_gst']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Items_details
        fields = ['item_name', 'price', 'quantity']

