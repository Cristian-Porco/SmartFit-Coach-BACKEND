# Generated by Django 4.2.4 on 2025-04-22 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_rename_tempo_gymplansetdetail_tempo_fcr'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gymplansetdetail',
            old_name='actual_reps',
            new_name='actual_reps_1',
        ),
        migrations.RenameField(
            model_name='gymplansetdetail',
            old_name='prescribed_reps',
            new_name='prescribed_reps_1',
        ),
        migrations.AddField(
            model_name='gymplansetdetail',
            name='actual_reps_2',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='gymplansetdetail',
            name='prescribed_reps_2',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
