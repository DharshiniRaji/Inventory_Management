# Generated by Django 5.0.12 on 2025-03-02 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("InventoryManagementApp", "0004_buyer_bill"),
    ]

    operations = [
        migrations.CreateModel(
            name="BillItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("item_name", models.CharField(max_length=255)),
                ("price", models.FloatField()),
                ("quantity", models.IntegerField()),
                (
                    "bill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="InventoryManagementApp.bill",
                    ),
                ),
            ],
        ),
    ]
