from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0009_series_roles"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganizationSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(
                    blank=True,
                    default="",
                    help_text='Zum Beispiel „Fachbereich 20“. Die Angabe erscheint in der Anwendungs-Kopfzeile und in Protokollen.',
                    max_length=160,
                    verbose_name="Organisationseinheit",
                )),
            ],
            options={
                "verbose_name": "Organisationseinstellung",
                "verbose_name_plural": "Organisationseinstellungen",
            },
        ),
    ]
