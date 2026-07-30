from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User Model extending AbstractUser.
    Keeps the model clean and future-ready for custom fields.
    """
    pass
