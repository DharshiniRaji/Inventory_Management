from django.contrib import admin
from django.urls import path
from .views import Index, SignUpView, Dashboard, AddItem, EditItem, DeleteItem, InventoryOption
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="inventory/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="inventory/logout.html"), name="logout"),
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    
    # Inventory Management
    path("add-item/", AddItem.as_view(), name="add-item"),
    path("edit-item/<int:pk>/", EditItem.as_view(), name="edit-item"),
    path("delete-item/<int:pk>/", DeleteItem.as_view(), name="delete-item"),
    path("inventory_option/", InventoryOption.as_view(), name="inventory_option"),

    path('billing/', views.billing, name='billing'),
    path('bill_receipt/<int:bill_id>/', views.bill_receipt, name='bill_receipt'),
    path('generate_invoice/<int:bill_id>/', views.generate_invoice, name='generate_invoice'),  # New URL for invoice generation
]