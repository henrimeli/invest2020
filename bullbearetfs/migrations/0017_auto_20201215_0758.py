# Generated by Django 3.1.3 on 2020-12-15 07:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bullbearetfs', '0016_auto_20201113_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexTrackerIssuer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('short_name', models.CharField(default='', max_length=20)),
                ('description', models.CharField(default='', max_length=150)),
                ('website', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorDummy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default='', max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MajorIndexSymbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('short_name', models.CharField(default='', max_length=20)),
                ('description', models.CharField(default='', max_length=150)),
                ('symbol', models.CharField(default='', max_length=50)),
                ('website', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MarketDataProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=20)),
                ('website', models.CharField(default='', max_length=20)),
                ('connection_type', models.CharField(default='', max_length=20)),
                ('connection_API_Key', models.CharField(default='', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='MarketDummy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default='', max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Top15Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('price', models.FloatField(default=0)),
                ('symbol', models.CharField(default='', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='WebsiteContactPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default='', max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='notificationtype',
            name='aalue',
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='main_picture',
            field=models.ImageField(default='', upload_to='pic_folder/'),
        ),
        migrations.AddField(
            model_name='equityandmarketsentiment',
            name='composition_calc',
            field=models.CharField(choices=[('Random', 'Random'), ('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('A4', 'A4'), ('A5', 'A5'), ('A6', 'A6')], default='Random', max_length=25),
        ),
        migrations.AddField(
            model_name='equityandmarketsentiment',
            name='ignore_neutral_outcome',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='etfandreversepairrobot',
            name='regression_factor',
            field=models.CharField(choices=[('100,50,33', '100,50,33'), ('50,33,25', '50,33,25'), ('30,20,10', '30,20,10')], default='100,50,33', max_length=20),
        ),
        migrations.AlterField(
            model_name='equityandmarketsentiment',
            name='sentiment_feed',
            field=models.CharField(choices=[('Automatic', 'Automatic'), ('Manual', 'Manual'), ('Defer to Strategy', 'Defer to Strategy')], default='Manual', max_length=20),
        ),
        migrations.AlterField(
            model_name='etfpairrobotexecutiondata',
            name='order_client_id',
            field=models.CharField(blank=True, max_length=40, null=True),
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
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('settings_name', models.CharField(default='settings', max_length=20)),
                ('connection_request', models.BooleanField(default=False)),
                ('mentions', models.BooleanField(default=False)),
                ('receive_deal_updates', models.BooleanField(default=False)),
                ('receive_reminders', models.BooleanField(default=False)),
                ('receive_annoucements', models.BooleanField(default=False)),
                ('enable_two_step', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notifications_name', models.CharField(default='', max_length=20)),
                ('from_user', models.IntegerField(default=0)),
                ('to_user', models.IntegerField(default=0)),
                ('share_date', models.DateTimeField(auto_now_add=True)),
                ('read_date', models.DateTimeField(auto_now_add=True)),
                ('notification_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.notificationtype')),
            ],
        ),
        migrations.CreateModel(
            name='MarketInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('description', models.CharField(default='', max_length=150)),
                ('market_top_news', models.CharField(default='', max_length=150)),
                ('market_reference_links', models.CharField(default='', max_length=150)),
                ('symbol', models.CharField(default='', max_length=10)),
                ('market_type', models.CharField(choices=[('Equity', 'Equity'), ('Forex', 'Forex'), ('Crypto', 'Crypto'), ('Futures', 'Futures'), ('Commodity', 'Commodity')], default='Equity', max_length=25)),
                ('market_business_times', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.marketbusinesshours')),
            ],
        ),
        migrations.CreateModel(
            name='IndexTrackerETFSymbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('symbol', models.CharField(default='', max_length=10)),
                ('is_leveraged', models.BooleanField(default=True)),
                ('leveraged_coef', models.IntegerField(default=1)),
                ('average_volume', models.IntegerField(default=0)),
                ('average_daily_volatility', models.CharField(choices=[('10', '10%'), ('20', '20%'), ('30', '30%')], default='Investor', max_length=25)),
                ('etf_issuer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.indextrackerissuer')),
                ('followed_index', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.majorindexsymbol')),
            ],
        ),
        migrations.CreateModel(
            name='EquityTradingRobot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('description', models.CharField(default='', max_length=100)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('modify_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date modified')),
                ('internal_name', models.CharField(blank=True, default='', max_length=10)),
                ('sell_remaining_before_buy', models.BooleanField(default=False)),
                ('liquidate_on_next_opportunity', models.BooleanField(default=False)),
                ('visibility', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('deployed', models.BooleanField(default=False)),
                ('version', models.CharField(default='', max_length=10)),
                ('max_asset_hold_time', models.CharField(choices=[('1', '1'), ('5', '5'), ('14', '14'), ('21', '21'), ('30', '30')], default='1', max_length=5)),
                ('hold_time_includes_holiday', models.BooleanField(default=False)),
                ('live_data_check_interval', models.IntegerField(default=60)),
                ('data_feed_frequency', models.CharField(choices=[('minute', 'minute'), ('hour', 'hour'), ('day', 'day')], default='day', max_length=10)),
                ('orders', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.ordersmanagement')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.customer')),
                ('portfolio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.portfolio')),
                ('strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.equitystrategy')),
                ('symbols', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.robotequitysymbols')),
            ],
        ),
        migrations.CreateModel(
            name='EquityIndicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('description', models.CharField(default='', max_length=100)),
                ('indicator_class', models.CharField(choices=[('Manual Indicator', 'Manual Indicator'), ('Technical Indicator', 'Technical Indicator'), ('Volume Indicator', 'Volume Indicator'), ('Time Indicator', 'Time Indicator'), ('Profit Indicator', 'Profit Indicator'), ('Circuit Breaker', 'Circuit Breaker'), ('Immediate Indicator', 'Immediate Indicator')], default='Time Indicator', max_length=25)),
                ('indicator_family', models.CharField(choices=[('SMA', 'Simple Moving Average'), ('EMA', 'Exponential Moving Average'), ('OSC', 'Oscillator'), ('RSA', 'Relative Strength Index'), ('Fibonacci', 'Fibonacci'), ('STD', 'Standard Deviation'), ('Triggers', 'Triggers')], default='Triggers', max_length=25)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('modify_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('visibility', models.BooleanField(default=True)),
                ('treshold_to_market_open', models.CharField(choices=[('5', '5'), ('15', '15'), ('30', '30'), ('45', '45'), ('60', '60')], default='15', max_length=25)),
                ('treshold_to_volume_open', models.CharField(choices=[('1 Million', '1 Million'), ('2 Millions', '2 Millions')], default='1 Million', max_length=25)),
                ('volume_interval', models.CharField(choices=[('10% Average Volume', '10% Average Volume'), ('15% Average Volume', '15% Average Volume'), ('20% Average Volume', '20% Average Volume'), ('25% Average Volume', '25% Average Volume')], default='10% Average Volume', max_length=25)),
                ('time_interval', models.CharField(choices=[('30', '30'), ('45', '45'), ('60', '60'), ('90', '90'), ('120', '120')], default='60', max_length=25)),
                ('reset_on_start', models.BooleanField(default=True)),
                ('reset_daily', models.BooleanField(default=True)),
                ('use_robot_symbol', models.BooleanField(default=True)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.customerbasic')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bullbearetfs.customer')),
            ],
        ),
    ]