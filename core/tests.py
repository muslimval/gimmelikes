from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from .models import SiteConfiguration

class SiteConfigurationTestCase(TestCase):
    def setUp(self):
        self.config = SiteConfiguration.objects.create(
            site_name="Test Site",
            maintenance_mode=False,
            welcome_message="Welcome to the test site",
            footer_text="Test footer"
        )

    def test_site_configuration_creation(self):
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        self.assertEqual(self.config.site_name, "Test Site")
        self.assertFalse(self.config.maintenance_mode)

    def test_site_configuration_update(self):
        self.config.maintenance_mode = True
        self.config.save()
        updated_config = SiteConfiguration.objects.get(id=self.config.id)
        self.assertTrue(updated_config.maintenance_mode)

class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpassword'))

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'testuser')