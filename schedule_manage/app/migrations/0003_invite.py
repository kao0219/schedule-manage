# Generated by Django 5.1.7 on 2025-04-06 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_customuser_create_at_customuser_update_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invite_token', models.CharField(editable=False, max_length=255, unique=True)),
                ('status', models.IntegerField(default=1)),
                ('expires_at', models.DateTimeField()),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
