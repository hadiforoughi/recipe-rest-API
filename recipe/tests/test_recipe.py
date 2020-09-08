from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from PIL import Image
import tempfile
import os
RECIPE_URL = reverse('recipe:recipe-list')


def sample_tag(user, name='test'):
    """create sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='test'):
    """create sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def recipe_detail_url(id):
    """create sample url for recipe detail"""
    return reverse('recipe:recipe-detail', args=[id])


def recipe_upload_url(id):
    """create sample url for uploading image """
    return reverse('recipe:recipe-upload-image',args=[id])

def sample_recipe(user, **params):
    """create sample recipe"""
    default = {
        'title': 'test',
        'time_minutes': 5,
        'price': 10.00
    }
    default.update(params)
    return Recipe.objects.create(user=user, **default)


class PublicRecipeTest(TestCase):
    """test recipe publicaly"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTests(TestCase):
    """test the authorized user recipe API"""

    def setUp(self):
        self.user = get_user_model().objects.create(
            email='test@gmail.com',
            password='pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """get recipe successfully"""
        sample_recipe(user=self.user)
        param = {'title': 'test2'}
        sample_recipe(user=self.user, **param)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-title')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """recipe must returned for own user"""
        user_test = get_user_model().objects.create(
            email='test2@gmail.com',
            password='pass1234'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=user_test)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-title')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_datial(self):
        """test detailed recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        recipe.ingredient.add(sample_ingredient(user=self.user))
        res = self.client.get(recipe_detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)


    def test_partial_update_recipe(self):
        """test updating recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user,name="test2")
        payload={
            'title': "tesssst",
            'tag' : [new_tag.id]
        }
        url = recipe_detail_url(recipe.id)
        self.client.patch(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        tags = recipe.tag.all()
        self.assertEqual(len(tags),1)
        self.assertIn(new_tag,tags)

    # def test_full_update_recipe(self):
    #     """test updating a recipe with put"""
    #     recipe = sample_recipe(user=self.user)
    #     recipe.tag.add(sample_tag(user=self.user))
    #     payload = {
    #         'title': "tesssst",
    #         'time_minutes': 34,
    #         'price' : 3.44
    #     }
    #     url = recipe_detail_url(recipe.id)
    #     self.client.put(url, payload)
    #     recipe.refresh_from_db()
    #
    #     self.assertEqual(recipe.title, payload['title'])
    #     self.assertEqual(recipe.time_minutes,payload['time_minutes'])
    #     self.assertEqual(recipe.price,payload['price'])
    #     tags = recipe.tag.all()
    #     self.assertEqual(len(tags),0)

class RecipeUploadImageTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test1234556'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_recipe(self):
        """test uploading image for recipe successfuly"""
        url = recipe_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB',(10,10))
            img.save(ntf,format='JPEG')
            ntf.seek(0)
            res = self.client.post(url,{'image':ntf},format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('image',res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))


    def test_upload_image_bad_request(self):
        """test uploading an invalid image"""
        url = recipe_upload_url(self.recipe.id)
        res = self.client.post(url,{'image' : 'bad image'},format='multipart')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)