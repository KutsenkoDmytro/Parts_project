# Generated by Django 3.2.19 on 2023-07-01 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20230701_1829'),
        ('system_emails', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailsendingfact',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='emailsendingfact',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='emailsendingfact',
            name='order',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='order'),
        ),
        migrations.AlterField(
            model_name='emailsendingfact',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system_emails.emailtype', verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='emailsendingfact',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='updated'),
        ),
        migrations.AlterField(
            model_name='emailtype',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='emailtype',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='is active'),
        ),
        migrations.AlterField(
            model_name='emailtype',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=64, verbose_name='email type name'),
        ),
        migrations.AlterField(
            model_name='emailtype',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='updated'),
        ),
    ]
