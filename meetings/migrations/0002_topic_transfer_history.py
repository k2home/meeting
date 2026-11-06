from django.conf import settings
from django.db import migrations, models
from django.db.migrations.operations.base import Operation
import django.db.models.deletion


class EnsureModelTable(Operation):
    """Create a model table only when it is not already present."""

    reduces_to_sql = True
    reversible = True

    def __init__(self, model_name):
        self.model_name = model_name

    def state_forwards(self, app_label, state):
        # The accompanying SeparateDatabaseAndState operation owns state changes.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        existing = schema_editor.connection.introspection.table_names()
        if model._meta.db_table not in existing:
            schema_editor.create_model(model)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        existing = schema_editor.connection.introspection.table_names()
        if model._meta.db_table in existing:
            schema_editor.delete_model(model)

    def describe(self):
        return f"Create {self.model_name} table if it does not exist"

    def deconstruct(self):
        return ("meetings.migrations.0002_topic_transfer_history.EnsureModelTable", [self.model_name], {})


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                EnsureModelTable("TopicTransferHistory"),
            ],
            state_operations=[
                migrations.CreateModel(
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
                    options={"verbose_name": "Themenübertragung", "verbose_name_plural": "Themenübertragungen", "ordering": ["-transferred_at"]},
                ),
            ],
        ),
    ]
