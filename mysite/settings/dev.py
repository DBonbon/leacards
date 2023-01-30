from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-l-^tupr!-ye9*n4sylkb)h+c#8bb8wa69-)dsx=pb!93w-j=w2"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
