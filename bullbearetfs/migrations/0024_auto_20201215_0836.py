# Generated by Django 3.1.3 on 2020-12-15 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bullbearetfs', '0023_auto_20201215_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etfpairrobotexecution',
            name='config_params',
            field=models.CharField(blank=True, default='', max_length=3500),
        ),
    ]