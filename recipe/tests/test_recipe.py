from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')

def sample_recipe(user,**params):
    """create sample recipe"""
    default = {
    'title' : 'test',
    'time_minutes' : 5,
    'price' : 10.00
    }
    default.update(params)
    return Recipe.objects.create(user=user,**default)


class PublicRecipeTest(TestCase):
    """test recipe publicaly"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTests(TestCase):
    """test the authorized user recipe API"""

    def setUp(self):
        self.user = get_user_model().objects.create(
        email = 'test@gmail.com',
        password = 'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_retrive_recipes(self):
        """get recipe successfully"""
        sample_recipe(user=self.user)
        param = {'title' : 'test2'}
        sample_recipe(user=self.user,**param)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-title')
        serializer = RecipeSerializer(recipes , many = True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)


    def test_recipe_limited_to_user(self):
        """recipe must returned for own user"""
        user_test = get_user_model().objects.create(
        email = 'test2@gmail.com',
        password = 'pass1234'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=user_test)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-title')
        serializer = RecipeSerializer(recipes,many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data,serializer.data)
