# Generated by Django 5.1.4 on 2025-05-31 23:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_memo_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='memo',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='memos', to=settings.AUTH_USER_MODEL),
        ),
    ]
