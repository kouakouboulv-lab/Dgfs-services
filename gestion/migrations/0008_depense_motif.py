from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0007_activite_motif'),
    ]

    operations = [
        migrations.AddField(
            model_name='depense',
            name='motif',
            field=models.CharField(
                max_length=255,
                blank=True,
                null=True
            ),
        ),
    ]