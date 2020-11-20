# Generated by Django 3.1.3 on 2020-11-13 18:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bullbearetfs', '0011_etfandreversepairrobot_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='RobotBudgetManagement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portfolio_initial_budget', models.FloatField(blank=True, default=0.0, null=True)),
                ('use_percentage_or_fixed_value', models.CharField(choices=[('Number', 'Number'), ('Percent', 'Percent')], default='Number', max_length=15)),
                ('current_cash_position', models.FloatField(default=0.0)),
                ('cash_position_update_policy', models.CharField(choices=[(24, '1 day'), (1, 'hourly'), (0, 'immediate'), (48, '2 days'), (72, '3 days')], default='daily', max_length=15)),
                ('add_taxes', models.BooleanField(default=False)),
                ('add_commission', models.BooleanField(default=False)),
                ('add_other_costs', models.BooleanField(default=False)),
                ('taxes_rate', models.CharField(choices=[('0', '0'), ('5', '5')], default='0', max_length=5)),
                ('commission_per_trade', models.CharField(choices=[('0', '0'), ('1', '1'), ('5', '5')], default='0', max_length=5)),
                ('other_costs', models.CharField(choices=[('0', '0'), ('5', '5')], default='0', max_length=5)),
                ('max_budget_per_purchase_percent', models.CharField(choices=[('10', '10'), ('15', '15'), ('20', '20'), ('25', '25'), ('30', '30')], default='15', max_length=15)),
                ('max_budget_per_purchase_number', models.CharField(choices=[('500', '500'), ('250', '250'), ('1000', '1000'), ('1500', '1500'), ('2000', '2000'), ('2500', '2500')], default='2000', max_length=15)),
                ('pair_robot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.etfandreversepairrobot')),
            ],
        ),
        migrations.CreateModel(
            name='EquityAndMarketSentiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_sentiment', models.CharField(choices=[(-3, '3x Bearish'), (-2, '2x Bearish'), (-1, '1x Bearish'), (0, 'Neutral'), (1, '1x Bullish'), (2, '2x Bullish'), (3, '3x Bullish')], default='Neutral', max_length=15)),
                ('market_sentiment', models.CharField(choices=[(-3, '3x Bearish'), (-2, '2x Bearish'), (-1, '1x Bearish'), (0, 'Neutral'), (1, '1x Bullish'), (2, '2x Bullish'), (3, '3x Bullish')], default='Neutral', max_length=15)),
                ('sector_sentiment', models.CharField(choices=[(-3, '3x Bearish'), (-2, '2x Bearish'), (-1, '1x Bearish'), (0, 'Neutral'), (1, '1x Bullish'), (2, '2x Bullish'), (3, '3x Bullish')], default='Neutral', max_length=15)),
                ('equity_sentiment', models.CharField(choices=[(-3, '3x Bearish'), (-2, '2x Bearish'), (-1, '1x Bearish'), (0, 'Neutral'), (1, '1x Bullish'), (2, '2x Bullish'), (3, '3x Bullish')], default='Neutral', max_length=15)),
                ('influences_acquisition', models.BooleanField(default=False)),
                ('external_sentiment_weight', models.CharField(choices=[(100, '100'), (50, '50'), (0, '0')], default='50', max_length=15)),
                ('market_sentiment_weight', models.CharField(choices=[(100, '100'), (50, '50'), (0, '0')], default='50', max_length=15)),
                ('sector_sentiment_weight', models.CharField(choices=[(100, '100'), (50, '50'), (0, '0')], default='50', max_length=15)),
                ('equity_sentiment_weight', models.CharField(choices=[(100, '100'), (50, '50'), (0, '0')], default='50', max_length=15)),
                ('sentiment_feed', models.CharField(choices=[('Automatic', 'Automatic'), ('Manual', 'Manual')], default='Manual', max_length=15)),
                ('circuit_breaker', models.BooleanField(blank=True, default=False)),
                ('pair_robot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.etfandreversepairrobot')),
            ],
        ),
    ]
