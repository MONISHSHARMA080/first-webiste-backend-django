from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError


class User_in_app(AbstractUser):
    class Meta:
        indexes = [
            models.Index(fields=['registered_date', 'email', 'username']),
            models.Index(fields=['email_verified','verified_through_auth_provider']),
            models.Index(fields=['otp','otp_created_at']),
            models.Index(fields=['profile_picture_url','password']),
        ]
    registered_date = models.DateTimeField(auto_now_add=True)
    
    profile_picture_url = models.URLField(null=True, blank=True)
    email_verified = models.BooleanField(null=False, blank=False, default=False)
    verified_through_auth_provider = models.BooleanField(null=False, blank=False, default=False)
    email = models.EmailField(null=False,blank=False,unique=True)
    username = models.CharField(null=False,blank=False,max_length=700)
    
    password = models.CharField(max_length=255, blank=True, null=True)
    
    otp = models.IntegerField( null=True, blank=True,)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    # ----try to remove them as don't need them
    groups = models.ManyToManyField(Group, related_name='magical_website_users')
    user_permissions = models.ManyToManyField(Permission, related_name='magical_website_user_permissions')
    
    
   

    
    # def __str__(self):
    #     return f"{self.username}"
    
