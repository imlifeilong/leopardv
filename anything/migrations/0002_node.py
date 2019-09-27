# Generated by Django 2.2.1 on 2019-09-27 01:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('anything', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('nid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(default=None, max_length=255)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('port', models.IntegerField(blank=True, default=6800, null=True)),
                ('status', models.IntegerField(blank=True, default=1, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('platform', models.CharField(default=None, max_length=255)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Node',
            },
        ),
    ]
