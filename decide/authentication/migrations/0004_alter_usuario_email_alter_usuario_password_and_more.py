# Generated by Django 4.1 on 2023-12-19 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_alter_usuario_options_alter_usuario_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='username',
            field=models.CharField(max_length=20),
        ),
    ]
