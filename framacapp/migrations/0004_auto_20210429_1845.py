# Generated by Django 3.2 on 2021-04-29 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('framacapp', '0003_auto_20210429_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='directory',
            name='parent',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='framacapp.directory'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='file',
            name='parent',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='framacapp.directory'),
            preserve_default=False,
        ),
    ]