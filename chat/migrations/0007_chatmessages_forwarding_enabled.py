# Generated by Django 4.1.7 on 2023-05-26 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_alter_chatmessages_pdf_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessages',
            name='forwarding_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
