from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0052_audit_history_query_indexes"),
    ]

    operations = [
        migrations.DeleteModel(name="EnaioDiagnosticReport"),
        migrations.DeleteModel(name="EnaioAgentLog"),
        migrations.DeleteModel(name="EnaioAgent"),
        migrations.DeleteModel(name="EnaioTransfer"),
        migrations.DeleteModel(name="EnaioFolderSelection"),
        migrations.DeleteModel(name="EnaioFilingTarget"),
        migrations.DeleteModel(name="EnaioSettings"),
    ]
