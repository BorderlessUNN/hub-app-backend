from django.test import TestCase

from accounts.models import CustomUser
from accounts.utils import normalize_phone_number
from helpers.exceptions import CustomValidationException


class NormalizePhoneNumberTests(TestCase):
    def test_local_leading_zero(self):
        self.assertEqual(normalize_phone_number("08012345678"), "+2348012345678")

    def test_country_code_no_plus(self):
        self.assertEqual(normalize_phone_number("2348012345678"), "+2348012345678")

    def test_country_code_with_plus(self):
        self.assertEqual(normalize_phone_number("+2348012345678"), "+2348012345678")

    def test_ten_digit_local(self):
        self.assertEqual(normalize_phone_number("8012345678"), "+2348012345678")

    def test_strips_spaces_and_dashes(self):
        self.assertEqual(normalize_phone_number("0801-234 5678"), "+2348012345678")

    def test_invalid_too_short(self):
        with self.assertRaises(CustomValidationException):
            normalize_phone_number("12345")

    def test_empty(self):
        with self.assertRaises(CustomValidationException):
            normalize_phone_number("")


class AdminRoleTests(TestCase):
    def test_create_admin_defaults_to_staff(self):
        admin = CustomUser.objects.create_admin(
            user_name="Front Desk", email="staff@example.com", password="pass1234",
        )
        self.assertEqual(admin.admin_role, CustomUser.AdminRole.STAFF)
        self.assertTrue(admin.is_superuser)
        self.assertFalse(admin.is_super_admin)

    def test_create_super_admin(self):
        admin = CustomUser.objects.create_admin(
            user_name="Boss", email="super@example.com", password="pass1234",
            admin_role=CustomUser.AdminRole.SUPER,
        )
        self.assertTrue(admin.is_super_admin)

    def test_no_hard_cap_on_admin_count(self):
        for i in range(4):
            CustomUser.objects.create_admin(
                user_name=f"Admin {i}", email=f"admin{i}@example.com", password="pass1234",
            )
        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 4)

    def test_member_phone_uniqueness_enforced(self):
        CustomUser.objects.create_user(
            email="m1@example.com", user_name="M1", is_member=True, phone_number="+2348012345678",
        )
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                email="m2@example.com", user_name="M2", is_member=True, phone_number="+2348012345678",
            )

    def test_non_member_phone_not_unique(self):
        # The unique constraint is conditional on is_member=True, so two
        # non-members may share a number without error.
        CustomUser.objects.create_user(
            email="n1@example.com", user_name="N1", is_member=False, phone_number="+2348012345678",
        )
        CustomUser.objects.create_user(
            email="n2@example.com", user_name="N2", is_member=False, phone_number="+2348012345678",
        )
        self.assertEqual(CustomUser.objects.filter(phone_number="+2348012345678").count(), 2)
