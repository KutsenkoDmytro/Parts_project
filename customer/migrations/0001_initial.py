# Generated by Django 3.2.19 on 2023-07-01 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('edrpou_code', models.IntegerField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'company',
                'verbose_name_plural': 'companies',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100)),
                ('position', models.CharField(max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees_company', to='customer.company')),
            ],
            options={
                'verbose_name': 'employee',
                'verbose_name_plural': 'employees',
                'ordering': ('last_name',),
                'unique_together': {('company', 'first_name', 'last_name', 'middle_name')},
            },
        ),
        migrations.CreateModel(
            name='Holding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'holding',
                'verbose_name_plural': 'holdings',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TechniqueType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'technique type',
                'verbose_name_plural': 'technique types',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Technique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=100, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='technique_company', to='customer.company')),
                ('technique_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='technique_technique_type', to='customer.techniquetype')),
            ],
            options={
                'verbose_name': 'technique',
                'verbose_name_plural': 'technique',
                'ordering': ('serial_number',),
            },
        ),
        migrations.AddField(
            model_name='company',
            name='holding',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='companies_holding', to='customer.holding'),
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('is_deleted', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stocks_companies', to='customer.company')),
                ('responsible_person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stocks_employee', to='customer.employee')),
            ],
            options={
                'verbose_name': 'stock',
                'verbose_name_plural': 'stocks',
                'ordering': ('name',),
                'unique_together': {('company', 'name')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='company',
            unique_together={('holding', 'name')},
        ),
    ]
