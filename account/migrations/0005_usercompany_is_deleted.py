# Generated by Django 3.2.19 on 2023-07-23 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20230723_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercompany',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
