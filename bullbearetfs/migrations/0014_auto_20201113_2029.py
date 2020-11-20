# Generated by Django 3.1.3 on 2020-11-13 20:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bullbearetfs', '0013_robotactivitywindow'),
    ]

    operations = [
        migrations.CreateModel(
            name='ETFPairRobotExecution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('exec_start_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('exec_end_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('config_params', models.CharField(blank=True, default='', max_length=500)),
                ('result_data', models.CharField(blank=True, default='', max_length=100)),
                ('execution_name', models.CharField(blank=True, default='', max_length=100)),
                ('execution_pace', models.CharField(choices=[('slow', 'slow'), ('medium', 'medium'), ('fast', 'fast')], default='medium', max_length=20)),
                ('visual_mode', models.BooleanField(default=False)),
                ('execution_status', models.CharField(choices=[('started', 'started'), ('inprogress', 'inprogress'), ('completed', 'completed'), ('not started', 'not started')], default='not started', max_length=20)),
                ('dispose_all_on_close', models.BooleanField(default=False)),
                ('robot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.etfandreversepairrobot')),
            ],
        ),
        migrations.AlterField(
            model_name='tradedataholder',
            name='buy_order_client_id',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AlterField(
            model_name='tradedataholder',
            name='sell_order_client_id',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='tradedataholder',
            name='winning_order_client_id',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.CreateModel(
            name='ETFPairRobotExecutionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('exec_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('exec_action', models.CharField(choices=[('buy', 'buy'), ('sell', 'sell')], default='buy', max_length=10)),
                ('exec_params', models.CharField(blank=True, default='', max_length=500)),
                ('cost_or_income', models.FloatField(default=0)),
                ('order_client_id', models.CharField(blank=True, max_length=40, null=True)),
                ('execution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.etfpairrobotexecution')),
            ],
        ),
        migrations.AddField(
            model_name='tradedataholder',
            name='execution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.etfpairrobotexecution'),
        ),
    ]
