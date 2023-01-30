from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

class CustomUser(AbstractUser):
    display_name = models.CharField(verbose_name=("Display name"), max_length=30, help_text=("Will be shown e.g. when commenting"))
    date_of_birth = models.DateField(verbose_name=("Date of birth"), blank=True, null=True)
    address1 = models.CharField(verbose_name=("Address line 1"), max_length=1024, blank=True, null=True)
    address2 = models.CharField(verbose_name=("Address line 2"), max_length=1024, blank=True, null=True)
    zip_code = models.CharField(verbose_name=("Postal Code"), max_length=12, blank=True, null=True)
    city = models.CharField(verbose_name=("City"), max_length=1024, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    phone_regex = RegexValidator(regex=r"^\+(?:[0-9]●?){6,14}[0-9]$", message=("Enter a valid international mobile phone number starting with +(country code)"))
    mobile_phone = models.CharField(validators=[phone_regex], verbose_name=("Mobile phone"), max_length=17, blank=True, null=True)
    additional_information = models.CharField(verbose_name=("Additional information"), max_length=4096, blank=True, null=True)
    photo = models.ImageField(verbose_name=("Photo"), upload_to='photos/', default='photos/default-user-avatar.png')

    class Meta:
        ordering = ['last_name']

    def get_absolute_url(self):
        return reverse('account_profile')

    def __str__(self):
        return f"{self.username}: {self.first_name} {self.last_name}"