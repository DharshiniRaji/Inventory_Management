# Generated by Django 5.0.12 on 2025-03-03 04:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("InventoryManagementApp", "0005_billitem"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bill",
            name="item_name",
        ),
        migrations.RemoveField(
            model_name="bill",
            name="price",
        ),
    ]
