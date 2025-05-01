# tests.py

from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
# from .models import Question, Answer

class UserRegistrationTestCase(APITestCase):
    def test_user_registration(self):
        url = "/api/register/"  # Adjust the URL for your registration endpoint
        data = {
            "username": "newtestuser",
            "email": "newtestuser@example.com",
            "password": "123#"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Ensure the user is created in the database
        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password("password123"))

class QuestionCreationTestCase(APITestCase):
    def setUp(self):
        self.client.login(username="testuser", password="456")

    def test_create_question(self):
        url = "/questions/"
        data = {
            "title": "How to test Django APIs?",
            "content": "I am looking for guidance on writing tests for Django APIs.",
            "tags": "Django, Testing"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.id)



