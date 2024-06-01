import os
import pyotp
from rest_framework import serializers,status

# from backend.views.views import verify_google_token
from google.oauth2 import id_token
from google.auth.transport import requests as Request_from_google_lib
from .models import User_in_app 
# password hashing --
from django.contrib.auth.hashers import make_password
import requests
import base64
from django.db import IntegrityError
from django.core.mail import send_mail
from first_website.settings import EMAIL_HOST_USER
from django.utils import timezone

class get_the_name_for_the_project(serializers.ModelSerializer):
    # user_name = serializers.CharField()
    prompt = serializers.CharField()
    class Meta:
        model = User_in_app
        fields = [
            # 'user_name',
                  'prompt'
                  ]
class temp_website_to_production_serializer(serializers.ModelSerializer):
    # user_name = serializers.CharField()
    prompt = serializers.CharField()
    class Meta:
        model = User_in_app
        fields = [
            # 'user_name',
                #   'prompt'
                  ]
        
class temp_website_generation_serializer(serializers.ModelSerializer):
    # user_name = serializers.CharField()
    prompt = serializers.CharField()
    class Meta:
        model = User_in_app
        fields = [
            # 'user_name',
                  'prompt'
                  ]
# ---temp
class View_all_users_serializer(serializers.ModelSerializer):
    class Meta:
        model = User_in_app
        fields = ['id', 'email', 'username', 'registered_date']  # Add other fields as needed
# ---temp
class verify_user_through_otp(serializers.ModelSerializer):
    otp = serializers.IntegerField(write_only=True,) 

    class Meta:
        model = User_in_app
        fields = ['otp','email']
        
    def update(self, instance, validated_data):
        otp = validated_data.get('otp')
        email = validated_data.get('email')
        try:
            user = User_in_app.objects.get(email=email)
        except User_in_app.DoesNotExist:
                return {"status":status.HTTP_404_NOT_FOUND,"message":validated_data}
        if user.email_verified == True:
            validated_data.pop('otp')
            validated_data['profile_picture_url'] = user.profile_picture_url 
            validated_data['email_verified'] = user.email_verified 
            validated_data['verified_through_auth_provider'] = user.verified_through_auth_provider 
            validated_data['username'] = user.username 
            return {"status": status.HTTP_201_CREATED, "message_to_display_user": "Your email has been verified , welcome onboard","message":"You are now verified","user":validated_data}

        if user.otp == otp:
            if user.otp_created_at and timezone.now() - user.otp_created_at <= timezone.timedelta(hours=2):
                user.email_verified = True
                user.save() 
                validated_data.pop('otp')
                validated_data['profile_picture_url'] = user.profile_picture_url 
                validated_data['email_verified'] = user.email_verified 
                validated_data['verified_through_auth_provider'] = user.verified_through_auth_provider 
                validated_data['username'] = user.username 
                
                return {"status": status.HTTP_201_CREATED, "message_to_display_user": "Your email has been verified , welcome onboard","message":"You are now verified","user":validated_data}
            else:
                totp = pyotp.TOTP(pyotp.random_base32())
                new_otp = totp.now()
                send_user_email(new_otp, user.email, user.username)
                # Update the OTP and OTP creation time
                user.otp = new_otp
                user.otp_created_at = timezone.now()
                user.save()
                return {"status": status.HTTP_400_BAD_REQUEST, "message_to_display_user": "OTP has expired. Please re-enter the new OTP"}
        else:
            return {"status": status.HTTP_400_BAD_REQUEST, "message_to_display_user": "Invalid OTP"}
      
    


class user_serializer(serializers.ModelSerializer):
    id_token = serializers.CharField(write_only=True,max_length=None, min_length=10, allow_blank=False, trim_whitespace=True) 

    class Meta:
        model = User_in_app
        fields = ['id_token']

    def create(self, validated_data):
        id_token = validated_data.pop('id_token') 
        response_from_google_auth_function = verify_google_token_view(id_token)
         
        if response_from_google_auth_function.get('status') == 400:
            # if the response from the google system is a bad request we will warn user that your token is invalid and message from google auth
            return {"status":400, "message":response_from_google_auth_function.get('exception') }
        #else if status is 200 
        elif response_from_google_auth_function.get('status') == 200:
            # fitting it in the model
            validated_data['username'] = response_from_google_auth_function.get('given_name')
            if validated_data['username'] =="": # why -> i am not sure if one of them m is empty or not  so just  to be safe    
                validated_data['username'] = response_from_google_auth_function.get('name') 
            validated_data['email'] = response_from_google_auth_function.get('email')
            validated_data['profile_picture_url'] = response_from_google_auth_function.get('picture', '')
            validated_data['email_verified'] = response_from_google_auth_function.get('email_verified', '')  
            validated_data['verified_through_auth_provider'] = response_from_google_auth_function.get('email_verified', '')    
            try :
                # super().create(validated_data)
                user = User_in_app.objects.create(**validated_data)
                # print('user object in the serilizers.py', user, "---", user.id)
                validated_data["id"] = user.id
            except IntegrityError as e: 
                if 'UNIQUE constraint' in str(e):
                    # if the user already exists just return it from there 
                    return return_already_existing_user_from_db_in_IntegrityError_of_unique_field(validated_data)                    
            return {"status":response_from_google_auth_function.get('status'),"user":validated_data}
   
class View_all_users_serializer(serializers.ModelSerializer):
    class Meta:
        model = User_in_app
        # fields = '__all__'
        exclude = ['groups','user_permissions','otp_created_at','is_active','is_staff','first_name','last_name','is_superuser','last_login','date_joined']
        
class Email_login_user_serializer(serializers.ModelSerializer):
    class Meta:
        model = User_in_app
        fields = ['email','password']
        # exclude = ['groups','user_permissions' , 'verified_through_auth_provider','email_verified','registered_date','otp','otp_created_at','last_name','first_name',]
            
    
    # def create(self, validated_data):
    #     # when if we have validated data just take it and just  hash the password(add salt)  before storing it
    #     validated_data['password'] =  make_password(validated_data.get('password'))
    #     totp = pyotp.TOTP(pyotp.random_base32())
    #     otp = totp.now()
    #     validated_data['otp'] =  otp
    #     validated_data['otp_created_at'] = timezone.now()
    #     validated_data['verified_through_auth_provider'] = False
    #     validated_data['email_verified'] = False
        
    #     # setting the email verified to be false by default here --not as it is set by defalut
    #     try :
    #         super().create(validated_data)
    #     except IntegrityError as e: 
    #             if 'UNIQUE constraint' in str(e):
    #                 # if the user already exists just return it from there 
    #                 return return_already_existing_user_from_db_in_IntegrityError_of_unique_field(validated_data) 
    #     validated_data.pop('password')
    #     validated_data.pop('otp')
    #     validated_data.pop('otp_created_at')
        
    #     send_user_email(otp, validated_data.get('email'), validated_data.get('username'))

    #     return {"status":200,"user":validated_data,"check_email_for_otp":True}
    
class Email_signup_usewr_serializer(serializers.ModelSerializer):
    class Meta:
        model = User_in_app
        fields = ['email','username','password']
        # exclude = ['groups','user_permissions' , 'verified_through_auth_provider','email_verified','registered_date','otp','otp_created_at','last_name','first_name',]
        
    def create(self, validated_data):
        # when if we have validated data just take it and just  hash the password(add salt)  before storing it
        validated_data['password'] =  make_password(validated_data.get('password'))
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()
        validated_data['otp'] =  otp
        validated_data['otp_created_at'] = timezone.now()
        validated_data['verified_through_auth_provider'] = False
        validated_data['email_verified'] = False
        
        # setting the email verified to be false by default here --not as it is set by defalut
        try :
            super().create(validated_data)
        except IntegrityError as e: 
                if 'UNIQUE constraint' in str(e):
                    # if the user already exists just return it from there 
                    return return_already_existing_user_from_db_in_IntegrityError_of_unique_field(validated_data) 
        validated_data.pop('password')
        validated_data.pop('otp')
        validated_data.pop('otp_created_at')
        
        send_user_email(otp, validated_data.get('email'), validated_data.get('username'))

        return {"status":200,"user":validated_data,"check_email_for_otp":True}
        
class Spotify_signup_user_serializer(serializers.ModelSerializer):
    id_token = serializers.CharField(write_only=True,max_length=None, min_length=10, allow_blank=False, trim_whitespace=True) 
    
    class Meta:
        model = User_in_app
        fields = ['id_token']
        # exclude = ['groups','user_permissions' , 'verified_through_auth_provider','email_verified','registered_date']
        
    def create(self, validated_data):
        
        # when if we have validated data just take it and just  hash the password(add salt)  before storing it
        code = validated_data.pop('id_token')
        
        redirect_uri = 'magicalfirstwebsite://'
        
        grant_type = 'authorization_code'
        client_id =  os.getenv('CLIENT_ID_SPOTIFY')
        client_secret = os.getenv('CLIENT_SECRET_SPOTIFY')
        
        authorization_without_encoding = F"{client_id}:{client_secret}"
        authorization = base64.b64encode(authorization_without_encoding.encode()).decode()
        url = 'https://accounts.spotify.com/api/token'
        data = {
            "form":{"grant_type":grant_type,"code":code,"redirect_uri":redirect_uri},
            "header":{"Authorization":f"Basic {authorization}"}
        }
        response = requests.post(url,data=data["form"],headers=data["header"])
        if response.status_code == 200:
            # now after getting access token from user's token , getting user details from the access token  
            access_token_for_getting_user_details_from_api = response.json().get('access_token')
            url_to_get_user_details_from_spotify = 'https://api.spotify.com/v1/me'
            response_containing_user_details = requests.get(url=url_to_get_user_details_from_spotify, headers={"Authorization": f"Bearer {access_token_for_getting_user_details_from_api}"})
            if response_containing_user_details.status_code == 200:
                status_code_to_send_in_response = response_containing_user_details.status_code
                response_containing_user_details = response_containing_user_details.json()
                
                validated_data['username'] = response_containing_user_details.get('display_name')
                validated_data['email'] = response_containing_user_details.get('email')
                images = response_containing_user_details.get('images')
                if images:
                    validated_data['profile_picture_url'] = images[0].get('url')
                validated_data['email_verified'] = 'True' # as we are using spotify's api
                validated_data['verified_through_auth_provider'] = 'True'
                try :
                    # super().create(validated_data)
                    user = User_in_app.objects.create(**validated_data)
                    validated_data['id'] = user.id
                    print(" in the try block (end--)")
                except IntegrityError as e: 
                    if 'UNIQUE constraint' in str(e):
                    # if the user already exists just return it from there 
                        return return_already_existing_user_from_db_in_IntegrityError_of_unique_field(validated_data) 
                # trying to return images inside  response ,a nd handeling the case of what to do if it is not there 
                if images:
                    validated_data['profile_picture_url'] = images[0].get('url')
                else:
                    validated_data['profile_picture_url'] = None
                return {"status":status_code_to_send_in_response,"message_to_display_user": "Your email has been verified , welcome onboard","message":"You are now verified","user":validated_data }
            else:
                print("\n what went wrong here in depth 2-->>", response_containing_user_details.content)
                return {"status":response.status_code,"message_to_display_user": "We can't verify you ,Please retry or try a different auth provider  ","message":"error during spotify api depth 2","user":validated_data} 

        else:
            if response.json().get('error_description') == "Invalid authorization code":
                return {"status":response.status_code,"message":response.json().get('error_description'),"message_to_display_user":"Please try logging in again your code has expired"}
        return {"status":response.status_code,"message":response.json().get('error_description')}
            
                
        
        
# auth helper function----------------
def verify_google_token(id_token_from_frontend: str):
    try:
        # Specify the Google client ID for your app
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        print(client_id , "<<---== client id")

        if client_id is None or len(client_id) < 2:
            print("\n\n\n '-------Error google client id is not provided ---------' \n\n\n")
            return 500, "We are unable to reach out to Google for auth"

        # Verify the token
        id_info = id_token.verify_oauth2_token(id_token_from_frontend, Request_from_google_lib.Request(), client_id)

        # Return the verification status or user information
        id_info['status'] = 200
        return id_info
    except Exception as e:
        # Token is invalid
        return {"status":400 , "exception": str(e)}
    
def verify_google_token_view(request_object):
        id_token_from_frontend = request_object
        print(f"id -token from the frontend -->>{id_token_from_frontend}")
        

        if not id_token_from_frontend:
            return { "message": "Bad request: id_token is missing", "status" : 400}

        # Calling the verify_google_token function
        response_from_google_auth_function = verify_google_token(id_token_from_frontend)
        print("response from the google auth func ->>",response_from_google_auth_function)
        
        return  response_from_google_auth_function



def return_already_existing_user_from_db_in_IntegrityError_of_unique_field(validated_data):
    """ will return already existing user if user try to create account again"""
    existing_user = User_in_app.objects.get(email=validated_data['email'])
    print( " in the  return_already_existing_user_from_db_in_IntegrityError_of_unique_field func", str(existing_user))
    return {
                "status": 200,
                "user":{
                "profile_picture_url": existing_user.profile_picture_url,
                "email_verified": existing_user.email_verified,
                "verified_through_auth_provider": existing_user.verified_through_auth_provider,
                "email": existing_user.email,
                "username": existing_user.username,
                "id":existing_user.id
                }
            }
    
def send_user_email(otp, user_email, user_name):
    subject = "OTP for your account"
    # HTML formatted message to make the top section bigger
    message = f"""
    <html>
    <head></head>
    <body>
        <h1 style="font-size: 24px;">Hi {user_name},</h1>
        <p><h3>Here's your OTP for your account verification :</h3></p>
        <h1 style="font-size: 36px;">{otp}</h1>
        <h4>OTP will be valid for 2 hours</h4>
    </body>
    </html>
    """
    recipient_list = [user_email]
    send_mail(subject, "", EMAIL_HOST_USER, recipient_list, html_message=message, fail_silently=False)
