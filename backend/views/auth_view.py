import os
from django.dispatch import Signal, receiver
from rest_framework.response import Response
from backend.models import User_in_app, logs_from_django
from backend.serializers import *
# from backend.serializers import Email_login_user_serializer, Email_signup_usewr_serializer, Spotify_signup_user_serializer, View_all_users_serializer, user_serializer,verify_user_through_otp
from rest_framework import mixins
from rest_framework import generics
from .views import verify_google_token
from rest_framework import status
# ---jwt---
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.serializers import View_all_users_serializer
from django.contrib.auth.hashers import check_password

class user_login_by_email(mixins.CreateModelMixin, generics.GenericAPIView):
    
    queryset = User_in_app.objects.all()
    serializer_class = Email_login_user_serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data )
        if not serializer.is_valid():
            ...
            # don't do anything as we know that user is in the db and 
            # return Response(  serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User_in_app.objects.get(email=serializer.data.get('email'))
        except ObjectDoesNotExist:
            return Response({"status":status.HTTP_404_NOT_FOUND, "message_to_display_user":"Email you enter was invalid","message":"user not found"})
        
        # check_password returns true or false
        if not check_password(serializer.data.get('password'),user.password):
            return Response({"status":status.HTTP_401_UNAUTHORIZED, "message_to_display_user":"Invalid auth credientials provided","message":"credientials provided is not valid"})
        response_to_return = {"status":status.HTTP_200_OK,"message_to_display_user":"Login successfull ! welcome"}
        # making the jwt token for the user
        refresh = RefreshToken.for_user(user)
        response_to_return["tokens"] = {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        return Response(response_to_return)    
    
class user_signup_by_email(mixins.CreateModelMixin, generics.GenericAPIView):
    
    queryset = User_in_app.objects.all()
    serializer_class = Email_signup_usewr_serializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data )
        if not serializer.is_valid():
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST)
            
        response_returned_by_serilizer_to_return_to_the_user = serializer.save()
        print(response_returned_by_serilizer_to_return_to_the_user,"---------------Response---")
        user_instance = User_in_app.objects.get(email=response_returned_by_serilizer_to_return_to_the_user['user']['email'])
        print("::::::::::::::;;;;;:::::",user_instance)
        # refresh = RefreshToken.for_user(user_instance)
        # print(refresh,"llllll")
        
        # token_serializer = TokenObtainPairSerializer()
        # print(token_serializer,"gggggg")
        
        # token_data = token_serializer.get_token(user_instance)
        # print(token_data,"aaaaaaAAAAAAAAAAAAA")
        # tokens = {
        #     'refresh': str(refresh),
        #     'access': str(token_data.access_token),
        # }
        # print(tokens,"BBbBBbbbBB")
        refresh = RefreshToken.for_user(user_instance)
        print("-----------------")
        print("-----------------")
        print({'statue' : 200,  'refresh':str(refresh), 'access':str(refresh.access_token) })
        print("-----------------")
        print("-----------------")
        # return Response({'statue' : 200,  'refresh':str(refresh), 'access':str(refresh.access_token) })
        return Response(response_returned_by_serilizer_to_return_to_the_user)    

class User(generics.GenericAPIView, mixins.ListModelMixin,mixins.DestroyModelMixin, mixins.RetrieveModelMixin,):
    queryset = User_in_app.objects.all()
    serializer_class = user_serializer
    # permission_classes = [IsAuthenticated]
    # authentication_classes=[JWTAuthentication]
    
    def post(self, request, *args, **kwargs):
        if os.getenv("GOOGLE_CLIENT_ID") == None or os.getenv("GOOGLE_CLIENT_ID") == "":
            print("\n\n ------==from view client id can't be found==------ \n\n")
        id = os.getenv("GOOGLE_CLIENT_ID")
        print(f"\n\n client id --->>  {id} \n\n")
        print("\n\n in the function before getting started \n\n")
        print(f"\n\n request object {request.data}  \n\n")
        
        serializer = self.get_serializer(data=request.data )
        if not serializer.is_valid():
            print("\n\n serilizer is not vlaid \n\n")
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST) 
        print("\n\n serilizer is vlaid and before save  \n\n")           
        serializer_response = serializer.save()
        print("\n\n response from create method --",serializer_response,"\n\n")
        serializer_response = add_JWT_token_for_user_in_response_from_serializer(serializer_response)
        print("\n\n response after JWT  --",serializer_response,"\n\n")
        user_created_create_temp_dir_in_sevelte_and_go.send(sender=self.__class__,user_name= serializer_response.get('user').get('username').replace(" ","") + str(serializer_response.get('user').get('id'))  )
        print("\n\n  before sending the response  \n\n")           
        print(serializer_response,"----00")

        return Response(serializer_response)
    

    def get(self, request, *args, **kwargs):
        print("hh---")
        users = User_in_app.objects.all()
        serializer = View_all_users_serializer(users, many=True)
        return Response(serializer.data)

    
    def delete(self, request, *args, **kwargs):
        users = self.get_queryset()
        users.delete()
        return Response( status=204)

    
class user_signup_by_spotify(mixins.CreateModelMixin, generics.GenericAPIView):
    
    queryset = User_in_app.objects.all()
    serializer_class = Spotify_signup_user_serializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data )
        print("\n\n from  spotify serilizer \n\n")
        if not serializer.is_valid():
            print("spotify serilizer is not valid ")
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST) 
        response_from_create_func_in_serilizer  = serializer.save()
        print(response_from_create_func_in_serilizer,"----from spotify serilizer")
        response_from_create_func_in_serilizer = add_JWT_token_for_user_in_response_from_serializer(response_from_create_func_in_serilizer)
        user_created_create_temp_dir_in_sevelte_and_go.send(sender=self.__class__,user_name= response_from_create_func_in_serilizer.get('user').get('username').replace(" ","")+str(response_from_create_func_in_serilizer.get('user').get('id'))  )
        return Response(response_from_create_func_in_serilizer) 
    
    
class verify_user_through_otp(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = User_in_app.objects.all()
    serializer_class = verify_user_through_otp
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User_in_app.objects.get(email=email)
        except User_in_app.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer_response = serializer.update(user, serializer.validated_data)
            serializer_response = add_JWT_token_for_user_in_response_from_serializer(serializer_response)
            return Response(serializer_response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
       

    
    
    
# ---helper function remove as we moved it to serilizers.py---
     
def verify_google_token_view(request_object):
        id_token_from_frontend = request_object.data.get('id_token')
        
        if not id_token_from_frontend:
            return { "message": "Bad request: id_token is missing", "status" : 400}
        # Calling the verify_google_token function
        id_info = verify_google_token(id_token_from_frontend)
        return  id_info
    
def add_JWT_token_for_user_in_response_from_serializer(serializer_response):
    
    """also adding check , if resp. from seri. is 200 do  if else return the object itself """
    
    if serializer_response.get('status') == 200 or serializer_response.get('status') == 201 :
        # ---------
        # making sure that even if google returns the 
        # ----------
        print(serializer_response.get('user').get('email'),"-- email fromt the add_JWT_token_for_user_in_response_from_serializer ")
        print("\n\n ===",serializer_response,"\n",serializer_response.get('user').get('email'),"-- email fromt the add_JWT_token_for_user_in_response_from_serializer ")
        user = User_in_app.objects.get(email=serializer_response.get('user').get('email'))
        refresh = RefreshToken.for_user(user)
        serializer_response["tokens"] = {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        return serializer_response
    else:
        return serializer_response
    


# ----------signals -----------

user_created_create_temp_dir_in_sevelte_and_go = Signal()


@receiver(signal=user_created_create_temp_dir_in_sevelte_and_go)
def create_temp_dir_for_newly_created_user(sender,user_name,**kwargs):
    print(user_name,"user name from user func")
    response = requests.post(os.getenv('NEXT_BACKEND_URL')+f"/create_temp_and_name_dir_for_user?userName={user_name}")
    print(response.content,"response content")
    if response.status_code != 200 or response.status_code != 201:
        from_the_request = str(f"Response status code: {response.status_code}, Content: {response.content}")
        logs_from_django.objects.create(log_string={"from_the_request":from_the_request,"user_name":user_name})
                