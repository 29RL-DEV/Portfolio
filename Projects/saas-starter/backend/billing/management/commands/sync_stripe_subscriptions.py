"""
Management command to sync subscription data from Stripe.
Useful for fixing inconsistencies or recovering from errors.
"""
import logging
import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from users.models import Profile

logger = logging.getLogger("billing")
stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = 'Sync subscription data from Stripe for all users with stripe_subscription_id'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Sync only a specific user by ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Get profiles to sync
        if user_id:
            profiles = Profile.objects.filter(
                user__id=user_id,
                stripe_subscription_id__isnull=False
            )
        else:
            profiles = Profile.objects.filter(
                stripe_subscription_id__isnull=False
            ).exclude(stripe_subscription_id='')

        total = profiles.count()
        self.stdout.write(f'Found {total} profiles with subscription IDs to sync')

        updated = 0
        errors = 0

        for profile in profiles:
            try:
                # Fetch subscription from Stripe
                subscription = stripe.Subscription.retrieve(profile.stripe_subscription_id)

                # Determine status
                status = subscription.status
                is_active = status == 'active'
                plan = 'pro' if is_active else 'free'

                if dry_run:
                    self.stdout.write(
                        f'Would update {profile.user.username}: '
                        f'status={status}, is_active={is_active}, plan={plan}'
                    )
                else:
                    # Update profile
                    profile.is_subscribed = is_active
                    profile.subscription_status = status
                    profile.plan = plan
                    profile.current_period_start = timezone.datetime.fromtimestamp(
                        subscription.current_period_start,
                        tz=timezone.utc
                    )
                    profile.current_period_end = timezone.datetime.fromtimestamp(
                        subscription.current_period_end,
                        tz=timezone.utc
                    )
                    profile.save()

                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated {profile.user.username}: {status}'
                        )
                    )

            except stripe.error.StripeError as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Stripe error for {profile.user.username}: {e}'
                    )
                )
                logger.error(f"Stripe error syncing subscription for user {profile.user.id}: {e}")

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Error syncing {profile.user.username}: {e}'
                    )
                )
                logger.error(f"Error syncing subscription for user {profile.user.id}: {e}", exc_info=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSync complete: {updated} updated, {errors} errors'
            )
        )
