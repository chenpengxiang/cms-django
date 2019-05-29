from django.db import models
from django.conf import settings
from .site import Site
from .organization import Organization


class User(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    regions = models.ManyToManyField(Site)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
