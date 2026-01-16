"""
Reconcile subscriptions between local database and Stripe.
Ensures our records are in sync with Stripe (authoritative source).
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from users.models import Profile
import stripe

logger = logging.getLogger('billing')
stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = 'Reconcile local subscription status with Stripe. Sync authoritative source.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Reconcile specific user (default: all)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without modifying'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))

        # Get profiles to reconcile
        if user_id:
            profiles = Profile.objects.filter(user_id=user_id)
            self.stdout.write(f'Reconciling user {user_id}...')
        else:
            # Only reconcile users with Stripe accounts
            profiles = Profile.objects.filter(
                stripe_customer_id__isnull=False
            ).exclude(stripe_customer_id='')
            self.stdout.write(f'Reconciling {profiles.count()} profiles...')

        reconciled = 0
        errors = 0
        no_changes = 0

        for profile in profiles:
            try:
                changed = self._reconcile_profile(profile, dry_run)
                if changed:
                    reconciled += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ User {profile.user.username}: {profile.subscription_status}'
                        )
                    )
                else:
                    no_changes += 1
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ User {profile.user.username}: {e}'
                    )
                )
                logger.error(f'Reconciliation error for user {profile.user.id}: {e}', exc_info=True)

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total: {profiles.count()}')
        self.stdout.write(self.style.SUCCESS(f'Reconciled: {reconciled}'))
        self.stdout.write(f'No changes: {no_changes}')
        self.stdout.write(self.style.ERROR(f'Errors: {errors}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were made'))

    def _reconcile_profile(self, profile, dry_run=False):
        """
        Reconcile single profile with Stripe.
        Returns True if changes were made, False otherwise.
        """
        # Get authoritative status from Stripe
        stripe_sub = self._get_stripe_subscription(profile)

        if not stripe_sub:
            # No subscription in Stripe, should be inactive
            if profile.subscription_status != 'inactive':
                logger.warning(
                    f'User {profile.user.id} has local status {profile.subscription_status} '
                    f'but no subscription in Stripe'
                )
                if not dry_run:
                    profile.set_subscription_status('inactive')
                return True
            return False

        # Update based on Stripe status
        new_status = stripe_sub.get('status', 'inactive')
        current_status = profile.subscription_status

        if current_status != new_status:
            logger.info(
                f'User {profile.user.id} status mismatch: '
                f'local={current_status}, stripe={new_status}'
            )
            if not dry_run:
                profile.update_subscription_status(new_status)
            return True

        # Update billing dates from Stripe
        if not dry_run:
            current_period_start = stripe_sub.get('current_period_start')
            current_period_end = stripe_sub.get('current_period_end')

            if current_period_start and current_period_end:
                start = timezone.datetime.fromtimestamp(
                    current_period_start,
                    tz=timezone.utc
                )
                end = timezone.datetime.fromtimestamp(
                    current_period_end,
                    tz=timezone.utc
                )

                if profile.current_period_start != start or profile.current_period_end != end:
                    profile.current_period_start = start
                    profile.current_period_end = end
                    profile.save(update_fields=['current_period_start', 'current_period_end'])
                    return True

        return False

    def _get_stripe_subscription(self, profile):
        """
        Get subscription details from Stripe.
        Returns subscription object or None.
        """
        if not profile.stripe_subscription_id:
            return None

        try:
            subscription = stripe.Subscription.retrieve(profile.stripe_subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at': subscription.cancel_at,
                'canceled_at': subscription.canceled_at,
            }
        except stripe.error.InvalidRequestError:
            # Subscription doesn't exist in Stripe
            logger.warning(
                f'Subscription {profile.stripe_subscription_id} not found in Stripe'
            )
            return None
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error retrieving subscription: {e}', exc_info=True)
            raise
