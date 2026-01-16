"""
Management command to recover user accounts with inconsistent Stripe data.
Handles cases where:
- User has subscription ID but it no longer exists in Stripe
- User claims to be subscribed but Stripe says otherwise
- Multiple users have same Stripe customer/subscription ID
"""
import logging
import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from users.models import Profile
from django.contrib.auth.models import User

logger = logging.getLogger("users")
stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = 'Recover and fix user account inconsistencies with Stripe'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Recover only a specific user by ID',
        )
        parser.add_argument(
            '--check-orphaned',
            action='store_true',
            help='Check for orphaned Stripe customers (not linked to any user)',
        )
        parser.add_argument(
            '--fix-duplicates',
            action='store_true',
            help='Fix cases where multiple users have same Stripe customer ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        check_orphaned = options.get('check_orphaned', False)
        fix_duplicates = options.get('fix_duplicates', False)
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        if user_id:
            self._recover_single_user(user_id, dry_run)
        elif check_orphaned:
            self._check_orphaned_customers(dry_run)
        elif fix_duplicates:
            self._fix_duplicate_customers(dry_run)
        else:
            self._recover_all_users(dry_run)

    def _recover_single_user(self, user_id, dry_run):
        """Recover a single user's Stripe data"""
        try:
            profile = Profile.objects.get(user__id=user_id)
            user = profile.user

            self.stdout.write(f"Recovering user {user.username} (ID: {user_id})")

            if profile.stripe_customer_id:
                # Check if customer exists in Stripe
                try:
                    customer = stripe.Customer.retrieve(profile.stripe_customer_id)
                    self.stdout.write(self.style.SUCCESS(f"✓ Customer exists in Stripe: {customer.id}"))

                    # Check subscriptions
                    if profile.stripe_subscription_id:
                        try:
                            subscription = stripe.Subscription.retrieve(profile.stripe_subscription_id)
                            status = subscription.status
                            is_active = status == 'active'
                            
                            if not dry_run:
                                with transaction.atomic():
                                    profile.is_subscribed = is_active
                                    profile.subscription_status = status
                                    profile.save()
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✓ Subscription synced: {status} (active={is_active})"
                                )
                            )
                        except stripe.error.InvalidRequestError:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"⚠ Subscription {profile.stripe_subscription_id} not found in Stripe"
                                )
                            )
                            if not dry_run:
                                with transaction.atomic():
                                    profile.is_subscribed = False
                                    profile.stripe_subscription_id = None
                                    profile.save()
                except stripe.error.InvalidRequestError:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Customer {profile.stripe_customer_id} not found in Stripe"
                        )
                    )
                    if not dry_run:
                        with transaction.atomic():
                            profile.is_subscribed = False
                            profile.stripe_customer_id = None
                            profile.stripe_subscription_id = None
                            profile.save()
            else:
                self.stdout.write(self.style.WARNING("No Stripe customer linked"))

        except Profile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User {user_id} not found"))

    def _check_orphaned_customers(self, dry_run):
        """Check for Stripe customers not linked to any user"""
        self.stdout.write("Checking for orphaned Stripe customers...")
        
        try:
            customers = stripe.Customer.list(limit=100)
            orphaned_count = 0

            for customer in customers.auto_paging_iter():
                user_id = customer.get('metadata', {}).get('user_id')
                
                if not user_id:
                    orphaned_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"Orphaned customer: {customer.id} (no user_id in metadata)")
                    )
                else:
                    try:
                        User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        orphaned_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Orphaned customer: {customer.id} (user_id {user_id} doesn't exist)"
                            )
                        )

            self.stdout.write(f"Found {orphaned_count} orphaned customers")

        except stripe.error.StripeError as e:
            self.stdout.write(self.style.ERROR(f"Stripe error: {e}"))

    def _fix_duplicate_customers(self, dry_run):
        """Fix cases where multiple users have same Stripe customer ID"""
        self.stdout.write("Checking for duplicate Stripe customer IDs...")

        # Find duplicate customer IDs
        duplicates = (
            Profile.objects
            .exclude(stripe_customer_id__isnull=True)
            .exclude(stripe_customer_id='')
            .values('stripe_customer_id')
            .annotate(count=__import__('django.db.models', fromlist=['Count']).Count('id'))
            .filter(count__gt=1)
        )

        for dup in duplicates:
            customer_id = dup['stripe_customer_id']
            profiles = Profile.objects.filter(stripe_customer_id=customer_id)
            
            self.stdout.write(
                self.style.WARNING(
                    f"Duplicate customer {customer_id} assigned to {profiles.count()} users"
                )
            )

            # Keep first, reset others
            for profile in profiles[1:]:
                if not dry_run:
                    with transaction.atomic():
                        profile.stripe_customer_id = None
                        profile.stripe_subscription_id = None
                        profile.is_subscribed = False
                        profile.save()
                
                self.stdout.write(f"Reset customer for {profile.user.username}")

    def _recover_all_users(self, dry_run):
        """Recover all users with Stripe data"""
        self.stdout.write("Recovering all users with Stripe data...")

        profiles = Profile.objects.exclude(stripe_customer_id__isnull=True).exclude(stripe_customer_id='')
        total = profiles.count()
        
        self.stdout.write(f"Found {total} users to recover")

        recovered = 0
        errors = 0

        for profile in profiles:
            try:
                self._recover_single_user(profile.user.id, dry_run)
                recovered += 1
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f"Error recovering {profile.user.username}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Recovery complete: {recovered} recovered, {errors} errors")
        )
