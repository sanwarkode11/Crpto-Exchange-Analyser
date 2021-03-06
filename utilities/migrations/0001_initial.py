# Generated by Django 3.2.4 on 2021-06-07 13:41

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import localflavor.in_.models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address1', models.CharField(max_length=255)),
                ('address2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(help_text='This can be city, village, town etc or even same as district', max_length=100, verbose_name='Village/Town')),
                ('state', localflavor.in_.models.INStateField(max_length=2, verbose_name='State')),
                ('pincode', models.CharField(max_length=6, validators=[django.core.validators.MinLengthValidator(6)])),
            ],
        ),
        migrations.CreateModel(
            name='ProjectConfigurations',
            fields=[
                ('key', models.CharField(max_length=55, primary_key=True, serialize=False, verbose_name='Key')),
                ('_value', models.TextField(null=True, verbose_name='Value')),
                ('type', models.CharField(choices=[('S', 'string'), ('I', 'int'), ('D', 'decimal'), ('C', 'csv')], default='S', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalProjectConfigurations',
            fields=[
                ('key', models.CharField(db_index=True, max_length=55, verbose_name='Key')),
                ('_value', models.TextField(null=True, verbose_name='Value')),
                ('type', models.CharField(choices=[('S', 'string'), ('I', 'int'), ('D', 'decimal'), ('C', 'csv')], default='S', max_length=2)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical project configurations',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
