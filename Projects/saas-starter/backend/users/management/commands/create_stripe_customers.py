"""
Management command to create Stripe customers for users who don't have one.
Useful for fixing profiles created when Stripe customer creation failed.
"""
import logging
import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from users.models import Profile

logger = logging.getLogger("users")
stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = 'Create Stripe customers for users missing stripe_customer_id'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Create customer only for a specific user by ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Get profiles without Stripe customers
        if user_id:
            profiles = Profile.objects.filter(
                user__id=user_id,
                stripe_customer_id__isnull=True
            ) | Profile.objects.filter(
                user__id=user_id,
                stripe_customer_id=''
            )
        else:
            profiles = Profile.objects.filter(
                stripe_customer_id__isnull=True
            ) | Profile.objects.filter(stripe_customer_id='')

        total = profiles.count()
        self.stdout.write(f'Found {total} profiles without Stripe customers')

        created = 0
        errors = 0

        for profile in profiles:
            user = profile.user
            try:
                if dry_run:
                    self.stdout.write(
                        f'Would create Stripe customer for {user.username} ({user.email})'
                    )
                else:
                    with transaction.atomic():
                        customer = stripe.Customer.create(
                            email=user.email,
                            name=user.get_full_name() or user.username,
                            metadata={
                                "user_id": str(user.id),
                                "username": user.username
                            }
                        )
                        profile.stripe_customer_id = customer.id
                        profile.save()

                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created Stripe customer {customer.id} for {user.username}'
                            )
                        )
                        logger.info(f"Created Stripe customer {customer.id} for user {user.id}")

            except stripe.error.StripeError as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Stripe error creating customer for {user.username}: {e}'
                    )
                )
                logger.error(f"Stripe error creating customer for user {user.id}: {e}")

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Error creating customer for {user.username}: {e}'
                    )
                )
                logger.error(f"Error creating customer for user {user.id}: {e}", exc_info=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'\nComplete: {created} created, {errors} errors'
            )
        )
