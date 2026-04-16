import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloth', '0003_feedback'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Feedback',
            new_name='CustomerSupport',
        ),
        migrations.AlterField(
            model_name='customersupport',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='support',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
