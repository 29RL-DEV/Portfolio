# Generated migration for Profile model enhancements

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_created_at_profile_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='subscription_status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('past_due', 'Past Due'),
                    ('unpaid', 'Unpaid'),
                    ('canceled', 'Canceled'),
                    ('inactive', 'Inactive')
                ],
                default='inactive',
                help_text='Current subscription status',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='plan',
            field=models.CharField(
                choices=[
                    ('free', 'Free'),
                    ('pro', 'Pro')
                ],
                default='free',
                help_text='Current plan: free or pro',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='current_period_start',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Billing period start date'
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='current_period_end',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Billing period end date / next renewal date'
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='profile',
                to='auth.user'
            ),
        ),
    ]
