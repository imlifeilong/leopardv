# Generated by Django 2.2.1 on 2019-10-12 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20191011_1819'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='running',
        ),
        migrations.AddField(
            model_name='job',
            name='alive',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
