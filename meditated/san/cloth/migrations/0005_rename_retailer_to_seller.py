from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cloth', '0004_rename_feedback_to_customer_support'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='is_retailer',
            new_name='is_seller',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='retailer',
            new_name='seller',
        ),
    ]
