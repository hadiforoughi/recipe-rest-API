from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email="test@gmail.com",password="test123"):
    """create a sample user"""
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """ test creating user with email is successful"""
        email = 'test@gmial.com'
        password = "test123"
        user = get_user_model().objects.create_user(email=email,password=password)

        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ test email of user is normalized"""

        email = "het@GAmil.com"
        user = get_user_model().objects.create_user(email,"test123")
        self.assertEqual(user.email , email.lower())

    def test_new_user_invalid_email(self):
        """ create user with no email error """

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,"1234")

    def test_create_new_superuser(self):
        """ create new superuser """

        user = get_user_model().objects.create_superuser(
        'test@gmail.com',
        'pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """test the tag string representation"""
        tag = models.Tag.objects.create(
        user = sample_user(),
        name = 'vegan'
        )

        self.assertEqual(str(tag),tag.name)

    def test_ingredient_str(self):
        """test ingredient created and __str__ function returned correct"""
        ingredient = models.Ingredient.objects.create(
        name="ingredient",
        user=sample_user()
        )

        self.assertEqual(str(ingredient),ingredient.name)

    def test_recipe_str(self):
        """test recipe created and __str__ function returned correct"""
        recipe = models.Recipe.objects.create(
        user = sample_user(),
        title = "test",
        time_minutes = 5,
        price= 5.00
        )

        self.assertEqual(str(recipe),recipe.title)
