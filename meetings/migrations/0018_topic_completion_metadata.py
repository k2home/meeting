from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("meetings", "0017_organization_brand_colors")]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="completed_at",
            field=models.DateField(blank=True, null=True, verbose_name="Abschlussdatum"),
        ),
        migrations.AddField(
            model_name="topic",
            name="completion_note",
            field=models.TextField(blank=True, verbose_name="Abschlussvermerk"),
        ),
    ]
