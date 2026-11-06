from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class CreateModelIfNotExists(migrations.CreateModel):
    """Create the model table only when it is not already present."""

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.name)
        existing = schema_editor.connection.introspection.table_names()
        if model._meta.db_table not in existing:
            super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.name)
        existing = schema_editor.connection.introspection.table_names()
        if model._meta.db_table in existing:
            super().database_backwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        CreateModelIfNotExists(
            name="TopicTransferHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transferred_at", models.DateTimeField(auto_now_add=True)),
                ("note", models.CharField(blank=True, max_length=500, verbose_name="Notiz")),
                ("from_series", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="outgoing_topic_transfers", to="meetings.meetingseries")),
                ("to_series", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="incoming_topic_transfers", to="meetings.meetingseries")),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transfer_history", to="meetings.topic")),
                ("transferred_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Themenübertragung",
                "verbose_name_plural": "Themenübertragungen",
                "ordering": ["-transferred_at"],
            },
        ),
    ]
