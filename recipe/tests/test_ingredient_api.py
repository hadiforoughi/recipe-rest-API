from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicTestForIngredient(TestCase):
    """test publicaly Ingredient"""

    def setUp(self):
        self.client = APIClient()

    def test_user_must_login(self):
        """user must login then can acsess ingredient list"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateTestForIngredient(TestCase):
    """test privately Ingredient"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
        email = "test@gmail.com",
        password = "passs122"
        )
        self.client.force_authenticate(self.user)

    def test_get_all_ingredient(self):
        """ test anthenticated user must get all of ingredient"""
        Ingredient.objects.create(
        name = "dessert",
        user = self.user
        )
        Ingredient.objects.create(
        name = "frouti",
        user = self.user,
        )
        res = self.client.get(INGREDIENT_URL)
        ingredients=Ingredient.objects.all().order_by('-name')
        ingredient_srealizer = IngredientSerializer(ingredients,many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,ingredient_srealizer.data)

    def test_ingredient_limited(self):
        """ingredient must show for own user"""
        user = get_user_model().objects.create(
        email="test2@gmail.com",
        password = "test123455"
        )
        Ingredient.objects.create(
        name = "desert",
        user = user
        )
        ingredient = Ingredient.objects.create(
        name = "frouti",
        user = self.user
        )
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)

        def test_create_ingredient_successful(self):
            """test create ingredient successfuly"""
            payload = {
            'name' : 'test',
            'user' : self.user
            }
            res = self.client.post(INGREDIENT_URL,payload)
            exists = Ingredient.objects.filter(name=payload['name']).exists()
            self.assertTrue(exists)

        def test_create_ingredient_invalid(self):
            """test create ingredient with wrong value becomes fails"""
            payload = {
            'name' : '',
            'user' : self.user
            }
            res = self.client.post(INGREDIENT_URL,payload)

            self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)


    def test_retrieve_ingredients_assigned_recipe(self):
        """test retrieving ingredients that assigned to specific recipe"""
        recipe = Recipe.objects.create(
            user=self.user,
            title='test',
            time_minutes=23,
            price=23
        )
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="test"
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='test2'
        )
        recipe.ingredient.add(ingredient1)
        res = self.client.get(INGREDIENT_URL,{'assigned_only' : 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(serializer1.data,res.data)
        self.assertNotIn(serializer2.data,res.data)

    def test_retrieving_ingredients_assigned_unique(self):
        """test filtering ingredients by assigned returns unique items"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="test1"
        )
        Ingredient.objects.create(
            user=self.user,
            name="test2"
        )
        recipe1 = Recipe.objects.create(
            user=self.user,
            title="test1",
            time_minutes=2,
            price=23
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="test2",
            time_minutes=32,
            price=32
        )
        recipe1.ingredient.add(ingredient1)
        recipe2.ingredient.add(ingredient1)
        res = self.client.get(INGREDIENT_URL,{'assigned_only': 1})
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)