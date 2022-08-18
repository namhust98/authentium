# Generated by Django 3.2.12 on 2022-07-29 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentium_market', '0005_trader_trader_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='fees',
        ),
        migrations.AddField(
            model_name='tradingfee',
            name='account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='authentium_market.account'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='tradingfee',
            unique_together={('account', 'instrument')},
        ),
    ]