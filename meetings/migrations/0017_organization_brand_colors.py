from django.core.validators import RegexValidator
from django.db import migrations, models

HEX_REQUIRED = RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben.")
HEX_OPTIONAL = RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")


def migrate_legacy_accent_color(apps, schema_editor):
    OrganizationSettings = apps.get_model("meetings", "OrganizationSettings")
    for settings in OrganizationSettings.objects.all():
        settings.primary_color = settings.accent_color or "#00549F"
        settings.primary_color_light = settings.accent_color_light or ""
        settings.primary_color_dark = settings.accent_color_dark or ""
        settings.save(update_fields=["primary_color", "primary_color_light", "primary_color_dark"])


class Migration(migrations.Migration):
    dependencies = [("meetings", "0016_organization_accent_colors")]

    operations = [
        migrations.AddField(model_name="organizationsettings", name="primary_color", field=models.CharField(default="#00549F", help_text="Grundfarbe für Navigation, Links und primäre Schaltflächen.", max_length=7, validators=[HEX_REQUIRED], verbose_name="Primärfarbe")),
        migrations.AddField(model_name="organizationsettings", name="primary_color_light", field=models.CharField(blank=True, default="", help_text="Optional. Leer = Primärfarbe verwenden.", max_length=7, validators=[HEX_OPTIONAL], verbose_name="Primärfarbe – Hellmodus")),
        migrations.AddField(model_name="organizationsettings", name="primary_color_dark", field=models.CharField(blank=True, default="", help_text="Optional. Leer = Primärfarbe verwenden.", max_length=7, validators=[HEX_OPTIONAL], verbose_name="Primärfarbe – Dunkelmodus")),
        migrations.AddField(model_name="organizationsettings", name="secondary_color", field=models.CharField(default="#8FC5FF", help_text="Ergänzende Akzente, dezente Hervorhebungen und unterstützende Flächen.", max_length=7, validators=[HEX_REQUIRED], verbose_name="Sekundärfarbe")),
        migrations.AddField(model_name="organizationsettings", name="secondary_color_light", field=models.CharField(blank=True, default="", help_text="Optional. Leer = Sekundärfarbe verwenden.", max_length=7, validators=[HEX_OPTIONAL], verbose_name="Sekundärfarbe – Hellmodus")),
        migrations.AddField(model_name="organizationsettings", name="secondary_color_dark", field=models.CharField(blank=True, default="", help_text="Optional. Leer = Sekundärfarbe verwenden.", max_length=7, validators=[HEX_OPTIONAL], verbose_name="Sekundärfarbe – Dunkelmodus")),
        migrations.AddField(model_name="organizationsettings", name="tertiary_color", field=models.CharField(default="#FFCC00", help_text="Markierungen und besondere visuelle Hervorhebungen.", max_length=7, validators=[HEX_REQUIRED], verbose_name="Tertiärfarbe")),
        migrations.AddField(model_name="organizationsettings", name="tertiary_color_light", field=models.CharField(blank=True, default="", help_text="Optional. Leer = Tertiärfarbe verwenden.", max_length=7, validators=[HEX_OPTIONAL], verbose_name="Tertiärfarbe – Hellmodus")),
        migrations.AddField(model_name="organizationsettings", name="tertiary_color_dark", field=models.CharField(blank=True, default="", help_text="Optional. Leer = Tertiärfarbe verwenden.", max_length=7, validators=[HEX_OPTIONAL], verbose_name="Tertiärfarbe – Dunkelmodus")),
        migrations.RunPython(migrate_legacy_accent_color, migrations.RunPython.noop),
        migrations.RemoveField(model_name="organizationsettings", name="accent_color"),
        migrations.RemoveField(model_name="organizationsettings", name="accent_color_light"),
        migrations.RemoveField(model_name="organizationsettings", name="accent_color_dark"),
    ]
