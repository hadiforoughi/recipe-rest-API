from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

class PublicTagAPITest(TestCase):
    """test Tag publicaly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retriving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
        'test@gmail.com',
        'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """test retriving tags"""
        Tag.objects.create(user=self.user,name='vegan')
        Tag.objects.create(user=self.user,name='dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags,many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_tags_limited_to_user(self):
        """test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
        'test2@gmail.com',
        'pdd23213'
        )
        Tag.objects.create(user=user2,name='fruity')
        tag = Tag.objects.create(user=self.user,name = 'comfort food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag.name)

    def test_create_tag_successful(self):
        """test create new tag"""
        payload = {
            'name': 'name'
        }
        res = self.client.post(TAGS_URL,payload)
        exists = Tag.objects.filter(user=self.user,name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """test create tag with invalid tag data"""
        payload = {
            'name': ''
        }
        res = self.client.post(TAGS_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)


    def test_retrieve_tags_assigned_recipe(self):
        """test retrieving tags that assigned to specific recipe"""
        recipe = Recipe.objects.create(
            user=self.user,
            title='test',
            time_minutes=23,
            price=23
        )
        tag1 = Tag.objects.create(
            user=self.user,
            name="test"
        )
        tag2 = Tag.objects.create(
            user=self.user,
            name='test2'
        )
        recipe.tag.add(tag1)
        res = self.client.get(TAGS_URL,{'assigned_only' : 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(serializer1.data,res.data)
        self.assertNotIn(serializer2.data,res.data)

    def test_retrieving_tags_assigned_unique(self):
        """test filtering tags by assigned returns unique items"""
        tag1 = Tag.objects.create(
            user=self.user,
            name="test1"
        )
        Tag.objects.create(
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
        recipe1.tag.add(tag1)
        recipe2.tag.add(tag1)
        res = self.client.get(TAGS_URL,{'assigned_only': 1})
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
