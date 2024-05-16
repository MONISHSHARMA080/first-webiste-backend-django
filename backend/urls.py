from django.urls import path
from .views import views
from .views import auth_view

from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
    TokenVerifyView,
    TokenRefreshView
)


urlpatterns = [
    
    path('api/token/', TokenRefreshSlidingView.as_view(), name='token_obtain'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    
    path('signup/google', auth_view.User.as_view()  ),  
    path('signup/email', auth_view.user_signup_by_email.as_view() ),  
    path('login/email', auth_view.user_login_by_email.as_view() ),  
    path('signup/spotify', auth_view.user_signup_by_spotify.as_view() ),  
    path('signup/otp', auth_view.verify_user_through_otp.as_view() ),  
    path('llm', views.response_from_llm, name='response_from_llm'),  
    path('temp_website', views.temp_website_generation.as_view() ), 
    path('temp_website_to_production', views.temp_website_to_production.as_view() ), 
    path('delete_a_project_or_temp', views.delete_a_project_or_temp.as_view() ), 
    path('get_all_the_projects_of_the_user', views.get_all_the_projects_of_the_user.as_view() ), 
    path('get_the_name_for_the_project', views.get_the_name_for_the_project.as_view() ), 
    path('verify', views.verify_google_token, name='verify_google_token'),  # TF try to remove it 
]
