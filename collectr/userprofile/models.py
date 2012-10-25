# -*- coding: utf-8 -*-
"""
    Stores user's informations.

"""

from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

import base64
import uuid

def create_token(max_length=32):
    return base64.encodestring(str(uuid.uuid4())).replace('=', '')[:max_length]

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=32, blank=True, default=create_token)


