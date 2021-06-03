from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotAuthenticated, ValidationError

from django.http import JsonResponse
from django.db.utils import IntegrityError

from .models import MyUser, Content
from .backends import JWTAuthentication
from .serializers import LoginSerializer, RegistrationSerializer

def custom_exception_handler(exc, context):
    """Реагирует на исключение
    Если  IntegrityError(попытка регистрации под существующим username), возвращает 403
    Если ValidationError(неудачная попытка логина), возвращает 401"""
    if isinstance(exc, IntegrityError):
         return Response("", status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, ValidationError):
         return Response("", status=status.HTTP_401_UNAUTHORIZED)
    response = exception_handler(exc, context)
    return response


class RegistrationAPIView(APIView):
    """ Регистрация нового пользователя 
    Доступен всем пользователям"""
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def register_user(self, username, password, name, isTeacher=False):
        """Регистрация пользователя с именем username и паролем password
        Возвращает сериализатор пользователя"""
        user = {"username":username, "password":password, "name": name, "isTeacher": isTeacher}
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    def post(self, request):
        """Обработка post-запроса 
        Регистрирует пользователя из данных полученного json и вохвращает в json токен
        """  
        # print(request.data)
        serializer = self.register_user(
            request.data.get("username"), 
            request.data.get("password"),
            request.data.get("name"),
            request.data.get("isTeacher")
        )
        response = Response(
            {
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )
        response.set_cookie("Token", serializer.data.get("token", None))
        return response


class LoginAPIView(APIView):
    """ Авторизация пользователя 
    Доступен всем пользователям"""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """Обработка post-запроса
        Проверяет наличие пользователя с переданными в json данными
        Если такой пользователь сущетсвует, то возвращает json с токеном"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie("Token", serializer.data.get("token", None))
        return response 


class IsTeacherAPIView(APIView):
    """ Проверка на то, что пользователь является учителем
    Доступен всем пользователям"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Обработка post-запроса
        Проверяет, является ли пользователь с переданным токеном уучителем
        Если такой пользователь сущетсвует, то возвращает json с параметром isTeacher"""
        token = request.data.get("token")
        print("TOKEN = " + token)
        if(token != ''):
            isTeacher = MyUser.objects.get_user_from_token(token).first().isTeacher
        else:
            isTeacher = 'null'
        response = Response({"isTeacher": isTeacher}, status=status.HTTP_200_OK)
        return response 


class ContentAPIView(APIView):
    """ Проверка на то, что пользователь является учителем
    Доступен всем пользователям"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Обработка get-запроса
        Возвращает текст страницы"""
        response = Response({"text": Content.objects.first().text}, status=status.HTTP_200_OK)
        return response

    def post(self, request):
        """Обработка post-запроса
        Изменяет текст страницы, если пользователь является учителем
        В случае успеха возвращает 200, иначе 403"""
        token = request.data.get("token")
        isTeacher = MyUser.objects.get_user_from_token(token).first().isTeacher

        if isTeacher:
            new_text = request.data.get("text", None)
            content, _ = Content.objects.get_or_create()
            content.text = new_text
            content.save()
            response = Response(status=status.HTTP_200_OK)
        else:
            response = Response(status=status.HTTP_403_FORBIDDEN)

        return response 
