from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status


class AdminSiteTests (TestCase):

    def setUp(self):
        """ create superuser and user before starting test"""

        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
        email="hadi@gmail.com",
        password="1234"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
        email="test@gmial.com",
        password="123"
        )

    def test_users_listed(self):
        """test that listed in our user page"""

        url = reverse('admin:core_user_changelist')
        #get response
        res = self.client.get(url)

        self.assertContains(res,self.user.name)
        self.assertContains(res,self.user.email)

    def test_user_change_page(self):
        """user edit page works"""

        url = reverse("admin:core_user_change",args=[self.user.id])
        # get response
        res = self.client.get(url)

        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_create_user_page(self):
        """test create user page works"""
        url = reverse('admin:core_user_add')
        # get response
        res = self.client.get(url)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
