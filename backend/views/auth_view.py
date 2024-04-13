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



def view_all_users(request):
    users = User_in_app.objects.all()
    serializer = View_all_users_serializer(users, many=True)
    
    jwt_authentication = JWTAuthentication()
    token = jwt_authentication.authenticate_header(request)
    print("User:", "Token:", token)
    try:
        jwt_authentication = JWTAuthentication()
        token = jwt_authentication.authenticate_header(request)
        print("User:", "Token:", token)
        # token = jwt_authentication.authenticate_header(request)
        # aaa = jwt_authentication.get_user(jwt_authentication.get_validated_token(request))
        # print("User:",aaa, "     ", "Token:", token)
        # User is authenticated, continue with your logic here
        return JsonResponse({"mm":serializer.data})
    except AuthenticationFailed as e:
        # User is not authenticated
        print("Authentication failed:", e)
        return JsonResponse({"error": "Authentication failed"}, status=401)

######################----------##################

""" API FOR  UPDATING DELEATING AND UPDATING PROFILE IS NOT BEING MADE AS WE DON'T NEED THAT  """

######################----------##################

#--------Djnago jwt(simple)

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims
#         token['username'] = user.username
#         # ...

#         return token

# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer


# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)

#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }
# #--------Djnago jwt(simple)


# # ---using this in my view
# # class RegisterView(APIView):
# #     def post(self, request):
# #         serializer = UserRegistrationSerializer(data=request.data)
# #         if not serializer.is_valid():
# #             return Response({'statue' : 403, 'errors':serializer.errors, 'message':'something went wrong' })
        
# #         serializer.save()
# #         user = User.objects.get(username=serializer.data['username'])
# #         refresh = RefreshToken.for_user(user)
# #         refresh['username'] = user.username

# #         return Response({'statue' : 200,  'refresh':str(refresh), 'access':str(refresh.access_token) })


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

class User(generics.GenericAPIView, mixins.ListModelMixin,mixins.DestroyModelMixin, mixins.RetrieveModelMixin,):
    queryset = User_in_app.objects.all()
    serializer_class = user_serializer
    
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data )
        if not serializer.is_valid():
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST)            
        a = serializer.save()
        print(a,"----")
        
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
