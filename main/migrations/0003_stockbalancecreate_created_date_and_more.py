# Generated by Django 4.1.7 on 2023-08-03 11:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_stock_receipt_purchase_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="stockbalancecreate",
            name="created_date",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="stockbalancecreate",
            name="update_date",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]