from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloth', '0005_rename_retailer_to_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
    ]
