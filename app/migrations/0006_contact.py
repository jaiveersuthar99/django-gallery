# Generated by Django 3.1.7 on 2021-06-21 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20210612_0202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=244)),
                ('email_id', models.CharField(max_length=244)),
                ('contact_number', models.CharField(max_length=244)),
            ],
        ),
    ]
