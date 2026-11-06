from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_transfer_history_if_missing(apps, schema_editor):
    model = apps.get_model("meetings", "TopicTransferHistory")
    table_name = model._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()
    if table_name not in existing_tables:
        schema_editor.create_model(model)


def drop_transfer_history_if_present(apps, schema_editor):
    model = apps.get_model("meetings", "TopicTransferHistory")
    table_name = model._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()
    if table_name in existing_tables:
        schema_editor.delete_model(model)


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    create_transfer_history_if_missing,
                    drop_transfer_history_if_present,
                ),
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
