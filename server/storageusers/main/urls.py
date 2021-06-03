from django.urls import re_path, include  
from .views import RegistrationAPIView, LoginAPIView, IsTeacherAPIView, ContentAPIView

urlpatterns = [
    re_path(r'^register/?$', RegistrationAPIView.as_view(), name='user_registration'),
    re_path(r'^auth/?$', LoginAPIView.as_view(), name='user_login'),
    re_path(r'^is_teacher/?$', IsTeacherAPIView.as_view(), name='is_teacher'),
    re_path(r'^edit/content/?$', ContentAPIView.as_view(), name='content'),
]