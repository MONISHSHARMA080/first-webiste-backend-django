from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError


class User_in_app(AbstractUser):
    registered_date = models.DateTimeField(auto_now_add=True)
    
    profile_picture_url = models.URLField(null=True, blank=True)
    email_verified = models.BooleanField(null=False, blank=False, default=False)
    verified_through_auth_provider = models.BooleanField(null=False, blank=False, default=False)
    email = models.EmailField(null=False,blank=False,unique=True)
    username = models.CharField(null=False,blank=False,max_length=700)
    
    password = models.CharField(max_length=255, blank=True, null=True)
    
    otp = models.IntegerField( null=True, blank=True,)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    
    groups = models.ManyToManyField(Group, related_name='magical_website_users')
    user_permissions = models.ManyToManyField(Permission, related_name='magical_website_user_permissions')
    
    
    
    
    # def save(self, *args, **kwargs):
    #     # Check if the user is verified through the auth provider
    #     # Allow saving if the user is verified through the auth provider
    #     print("kkk->",self.email_verified,"jjj->", self.password )
    #     if self.password is None:
    #         if self.email_verified == True:
    #             print("worked))))))))))))00)0))00")
    #             super().save(*args, **kwargs)
    #     elif self.password is  not None:
    #         print("Cannot create user with null password and unverified through auth provider")
    
    #         super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.name}"
    
