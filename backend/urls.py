from django.urls import path
from .views import views
from .views import auth_view

from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
    TokenVerifyView,
    token_refresh
)


urlpatterns = [
    
    path('api/token/', TokenObtainSlidingView.as_view(), name='token_obtain'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_obtain'),
    path('api/token/refresh/', token_refresh, name='token_refresh'),
    path('', auth_view.view_all_users, name='token_refresh'),

    
    path('signup/google', auth_view.User.as_view()  ),  
    path('signup/email', auth_view.user_signup_by_email.as_view() ),  
    path('signup/spotify', auth_view.user_signup_by_spotify.as_view() ),  
    path('signup/otp', auth_view.verify_user_through_otp.as_view() ),  
    path('llm', views.response_from_llm, name='response_from_llm'),  
    path('verify', views.verify_google_token, name='verify_google_token'),  
]
