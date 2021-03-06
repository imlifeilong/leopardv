# Generated by Django 2.2.1 on 2019-09-30 03:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0010_auto_20190929_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('status', models.IntegerField(blank=True, default=1, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('project', models.CharField(default='', max_length=128)),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('stop_time', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete='models.CASCADE', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Job',
            },
        ),
    ]
