from types import SimpleNamespace

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from apps.accounts.admin.user import UserAdmin
from apps.accounts.models import User


class UserAdminSaveModelTestCase(TestCase):
    def setUp(self):
        self.admin = UserAdmin(User, AdminSite())

    def test_save_model_hashes_password_when_changed(self):
        user = User.objects.create_user(
            phone_number="+998900000010",
            password="OldPass123",
            full_name="Test User",
        )
        user.password = "NewPlainPass456"
        form = SimpleNamespace(changed_data=["password"])

        self.admin.save_model(request=None, obj=user, form=form, change=True)

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPlainPass456"))

    def test_save_model_keeps_hash_when_password_unchanged(self):
        user = User.objects.create_user(
            phone_number="+998900000011",
            password="OldPass123",
            full_name="Test User",
        )
        original_hash = user.password
        form = SimpleNamespace(changed_data=[])

        self.admin.save_model(request=None, obj=user, form=form, change=True)

        user.refresh_from_db()
        self.assertEqual(user.password, original_hash)
