# Generated by Django 2.1.7 on 2019-02-21 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Emissions', '0005_auto_20190221_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='link',
            field=models.URLField(blank=True, default='', null=True),
        ),
    ]
