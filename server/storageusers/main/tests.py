from django.test import TestCase
from random import randint
from .serializers import RegistrationSerializer

class UserListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Настройка контекста для теста"""
        number_of_users = 5
        for user_num in range(number_of_users):
            login = 'Username%s' % user_num 
            name = 'name%s' % user_num
            isTeacher = randint(0, 1)
            password = 'Password%s' % user_num
            user = {"username": login, "name": name, "isTeacher": isTeacher, "password": password}
            serializer = RegistrationSerializer(data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def signup(self, login, name, isTeacher, password):
        """Регистрация пользователя с именем name и паролем password"""
        resp = self.client.post('/register/', data={'username': login, 'name': name, 'isTeacher': isTeacher, 'password': password})
        return resp

    def login(self, login, password):
        """Авторизация пользователя с именем name и паролем password"""
        resp = self.client.post('/auth/', data={'username': login, 'password': password})
        return resp

    def test_correct_signup(self):
        """Тестирование регистрации пользователя с корректными данными"""
        resp = self.signup('Username6', 'name6', 1, 'Password6')
        self.assertEqual(resp.status_code, 201)

    def test_correct_login(self):
        """Тестирование авторизации пользователя с корректными данными"""
        resp = self.login('Username4', 'Password4')
        self.assertEqual(resp.status_code, 200)

    def test_incorrect_login(self):
        """Тестирование авторизации несуществущего пользователя"""
        resp = self.login('Username7', 'Password7')
        self.assertEqual(resp.status_code, 401)

    def test_signup_with_exists_username(self):
        """Тестирование регистрации существующего пользователя"""
        resp = self.signup('Username4', 'name4', 1, 'Password4')
        self.assertEqual(resp.status_code, 403)

    def test_signup_with_incorrect_credentials(self):
        """Тестирование регистрации пользователя с несоответствующими шаблону данными"""
        self.client.raise_request_exception = True
        # Пароль больше 12 символов
        resp = self.signup('Username7', 'name7', 0, 'Password638753893101')
        self.assertEqual(resp.status_code, 401)
        # Пароль меньше 6 символов
        resp = self.signup('Username41', 'name7', 0,'Pass')
        self.assertEqual(resp.status_code, 401)
        # Логин больше 30 символов
        resp = self.signup('Username7sdfasefgsrfhrcskidfhtasd', 'name7', 0, 'Password4')
        self.assertEqual(resp.status_code, 401)
        # Логин меньше 4 символов
        resp = self.signup('Use', 'name7', 0,'Password4')
        self.assertEqual(resp.status_code, 401)
        # Имя больше 30 символов
        resp = self.signup('Username7sdfasefgsrfhrcskidfhtasd', 'name7sdfasefgsrsefgsrfhrcskidfhtasd', 0, 'Password4')
        self.assertEqual(resp.status_code, 401)
        # Имя меньше 4 символов
        resp = self.signup('Use', 'nam', 0,'Password4')
        self.assertEqual(resp.status_code, 401)

    
