from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.models import User_in_app
from backend.serializers import Email_signup_usewr_serializer, Spotify_signup_user_serializer, View_all_users_serializer, user_serializer,verify_user_through_otp
from rest_framework import mixins
from rest_framework import generics
from .views import verify_google_token
from rest_framework import status
# ---jwt---
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.serializers import View_all_users_serializer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed

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
        refresh['username'] = user_instance.username
        print("-----------------")
        print("-----------------")
        print({'statue' : 200,  'refresh':str(refresh), 'access':str(refresh.access_token) })
        print("-----------------")
        print("-----------------")
        # return Response({'statue' : 200,  'refresh':str(refresh), 'access':str(refresh.access_token) })
        return Response(response_returned_by_serilizer_to_return_to_the_user)    

# @permission_classes([IsAuthenticated])
class User(generics.GenericAPIView, mixins.ListModelMixin,mixins.DestroyModelMixin, mixins.RetrieveModelMixin,):
    queryset = User_in_app.objects.all()
    serializer_class = user_serializer
    permission_classes = [IsAuthenticated]
    # authentication_classes=[JWTAuthentication]
    
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data )
        if not serializer.is_valid():
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST)            
        a = serializer.save()
        # a["tokens"] = 
        user = User_in_app.objects.get(email=a.get('user').get('email'))
        refresh = RefreshToken.for_user(user)
        a["tokens"] = {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
        print(a,"----00",refresh)
        
        return Response(a)
    
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
        if not serializer.is_valid():
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST) 
        response_from_create_func_in_serilizer  = serializer.save()
        print(response_from_create_func_in_serilizer,"----from spotify serilizer")
        
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
            a = serializer.update(user, serializer.validated_data)
            return Response(a)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
       

    
    
    
# ---helper function remove as we moved it to serilizers.py---
     
def verify_google_token_view(request_object):
        id_token_from_frontend = request_object.data.get('id_token')
        
        if not id_token_from_frontend:
            return { "message": "Bad request: id_token is missing", "status" : 400}

        # Calling the verify_google_token function
        id_info = verify_google_token(id_token_from_frontend)
        
        return  id_info
