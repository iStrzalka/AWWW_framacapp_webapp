# Generated by Django 3.2 on 2021-04-29 16:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('framacapp', '0004_auto_20210429_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='framacapp.directory'),
        ),
    ]