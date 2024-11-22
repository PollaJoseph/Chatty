from django.core.management.base import BaseCommand
from userdata.models import AccountVerificationToken, ResetPasswordToken, ResetPasswordSecureToken


class Command(BaseCommand):
    help = 'Deletes all expired tokens'

    def handle(self, *args, **kwargs):
        AccountVerificationToken.delete_expired_tokens()
        ResetPasswordToken.delete_expired_tokens()
        ResetPasswordSecureToken.delete_expired_tokens()
        self.stdout.write(self.style.SUCCESS('Successfully deleted expired tokens'))
