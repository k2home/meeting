from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("meetings", "0045_enaio_document_type")]

    operations = [
        migrations.RemoveField(
            model_name="enaiofolderselection",
            name="token_hash",
        ),
        migrations.RemoveField(
            model_name="enaiotransfer",
            name="token_hash",
        ),
    ]
