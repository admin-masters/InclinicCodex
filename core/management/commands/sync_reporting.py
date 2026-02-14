from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Placeholder for transaction-to-reporting sync; reporting flow will be implemented later."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Reporting sync is deferred. No records moved."))
