# Generated by Django 4.0.4 on 2022-06-01 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('context_text', '0035_alter_article_author_original_person_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkdataoutputlog',
            name='network_data_file_path',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='networkdataoutputlog',
            name='network_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]