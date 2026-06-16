from django.db import migrations


def create_groups(apps, schema_editor):

    Group = apps.get_model("auth", "Group")

    Group.objects.get_or_create(name="admin")
    Group.objects.get_or_create(name="user")


class Migration(migrations.Migration):

    dependencies = [
        ("gestion", "0005_alter_activite_mode_paiement"),  # garde le nom exact de ta migration précédente
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]