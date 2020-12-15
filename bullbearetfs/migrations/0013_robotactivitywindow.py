# Generated by Django 3.1.3 on 2020-11-13 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bullbearetfs', '0012_equityandmarketsentiment_robotbudgetmanagement'),
    ]

    operations = [
        migrations.CreateModel(
            name='RobotActivityWindow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_before_open', models.BooleanField(default=False)),
                ('trade_after_close', models.BooleanField(default=False)),
                ('trade_during_extended_opening_hours', models.BooleanField(default=False)),
                ('offset_after_open', models.CharField(choices=[('0', '0'), ('15', '15'), ('30', '30'), ('45', '45'), ('60', '60')], default='0', max_length=15)),
                ('offset_before_close', models.CharField(choices=[('0', '0'), ('15', '15'), ('30', '30'), ('45', '45'), ('60', '60')], default='0', max_length=15)),
                ('blackout_midday_from', models.CharField(choices=[('0', '0'), ('10', '10:00am'), ('11', '11:00am'), ('12', '12:00pm'), ('13', '13:00pm'), ('14', '2:00pm'), ('15', '3:00pm')], default='0', max_length=15)),
                ('blackout_midday_time_interval', models.CharField(choices=[('0', '0'), ('15', '15'), ('30', '30'), ('45', '45'), ('60', '60')], default='0', max_length=15)),
                ('live_data_feed', models.CharField(choices=[('Polygon', 'Polygon'), ('Not Yet Implemented', 'Not Yet Implemented')], default='Polygon', max_length=25)),
                ('pair_robot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.etfandreversepairrobot')),
            ],
        ),
    ]