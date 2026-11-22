from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0015_topic_due_date_to_agenda_item"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="accent_color",
            field=models.CharField(
                default="#00549F",
                help_text="Zentrale Akzentfarbe für die gesamte Anwendung (Format #RRGGBB).",
                max_length=7,
                validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben.")],
                verbose_name="Akzentfarbe",
            ),
        ),
        migrations.AddField(
            model_name="organizationsettings",
            name="accent_color_light",
            field=models.CharField(
                blank=True, default="",
                help_text="Optional. Leer = zentrale Akzentfarbe verwenden.",
                max_length=7,
                validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")],
                verbose_name="Akzentfarbe – Hellmodus",
            ),
        ),
        migrations.AddField(
            model_name="organizationsettings",
            name="accent_color_dark",
            field=models.CharField(
                blank=True, default="",
                help_text="Optional. Leer = zentrale Akzentfarbe verwenden.",
                max_length=7,
                validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")],
                verbose_name="Akzentfarbe – Dunkelmodus",
            ),
        ),
    ]
