# Generated by Django 4.1.7 on 2023-05-01 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_chatmessages_pdf_file_alter_chatmessages_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessages',
            name='pdf_file',
            field=models.FileField(blank=True, upload_to='images/doc/pdf'),
        ),
    ]
