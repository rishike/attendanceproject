# Generated by Django 3.1.5 on 2021-08-07 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20210806_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='captured',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
