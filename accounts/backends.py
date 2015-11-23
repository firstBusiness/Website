import imaplib
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError


def normalize_username(username):
    return username[:30].replace('.', '_')


class BaseAuth:
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class NormalAuth(BaseAuth):
    def authenticate(self, email=None, password=None):
        if email and password:
            email = email + '@enib.fr' if '@' not in email else email
            try:
                user = User.objects.get(email=email)
                if not check_password(password, user.password):
                    return None
                return user
            except User.DoesNotExist:
                return None


class ImapAuth(BaseAuth):
    def authenticate(self, email=None, password=None):
        if email and password:
            with imaplib.IMAP4_SSL('imap-eleves.enib.fr') as srv:
                srv._mode_utf8()

                username = normalize_username(email.split("@")[0].strip())
                email = email.strip() + '@enib.fr' if '@' not in email else email
                user = None
                try:
                    srv.login(username, password)
                    user = User.objects.create_user(username, email, password)
                    enib_group = Group.objects.get(name='Enib')
                    enib_group.user_set.add(user)
                    user.save()
                except (imaplib.IMAP4.error, IntegrityError):
                    pass
                return user
