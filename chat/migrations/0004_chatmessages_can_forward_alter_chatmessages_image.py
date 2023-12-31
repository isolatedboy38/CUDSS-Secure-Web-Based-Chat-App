# Generated by Django 4.1.7 on 2023-04-30 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_chatmessages_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessages',
            name='can_forward',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='chatmessages',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/'),
        ),
    ]
