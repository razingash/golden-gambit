import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from stock.models import Company, Player
from stock.serializers import RegisterSerializer, DividedCompanySerializer, CompanyUpdateSerializer, \
    CompanyCreateSerializer, GoldAmountSerializer, ProductsTradingSerializer, CompanyTransmutationSerializer


@pytest.mark.django_db
class RegisterSerializerTestCase(TestCase):
    def test_valid_password(self):
        password = "kovarex907"
        try:
            RegisterSerializer.validate_password(password)
        except ValidationError:
            self.fail("validate_password raised ValidationError unexpectedly")

    def test_invalid_password(self):
        invalid_password = "kova"
        serializer = RegisterSerializer(data={"username": "djangobot0", "password": invalid_password})
        with self.assertRaises(ValidationError):
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

    def test_valid_username(self):
        username = "kovarex"
        try:
            RegisterSerializer.validate_username(username)
        except ValidationError:
            self.fail("validate_username raised ValidationError unexpectedly")

    def test_short_username(self):
        invalid_username = "kova"
        with self.assertRaises(ValidationError):
            RegisterSerializer.validate_username(invalid_username)

    def test_invalid_username_with_special_characters(self):
        invalid_username = "kovar%"
        with self.assertRaises(ValidationError):
            RegisterSerializer.validate_username(invalid_username)

    def test_create_user(self):
        data = {
            'username': 'kovarex',
            'password': 'kovarex907'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, data['username'])
        self.assertNotEqual(user.password, data['password'])
        self.assertTrue(user.check_password(data['password']))


@pytest.mark.django_db
class DividedCompanySerializerTestCase(TestCase):
    def test_get_isHead_authenticated_user(self):
        company = Company.objects.get(id=1)
        user = Player.objects.get(username='djangobot1')
        serializer = DividedCompanySerializer(company, context={'user': user})
        self.assertTrue(serializer.data['isHead'])

    def test_get_isHead_authenticated_user_not_head(self):
        company = Company.objects.get(id=1)
        user = Player.objects.get(username='djangobot2')
        serializer = DividedCompanySerializer(company, context={'user': user})
        self.assertFalse(serializer.data['isHead'])


@pytest.mark.django_db
class CompanyUpdateSerializerTestCase(TestCase):
    def test_update_name(self):
        company = Company.objects.get(id=1)
        serializer = CompanyUpdateSerializer(company, data={'name': 'Changed Name'}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_company = serializer.save()
        self.assertEqual(updated_company.name, 'Changed Name')

    def test_update_dividendes_percent_valid(self):
        company = Company.objects.get(id=1)
        serializer = CompanyUpdateSerializer(company, data={'dividendes_percent': 3}, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_dividendes_percent_too_low(self):
        company = Company.objects.get(id=1)
        serializer = CompanyUpdateSerializer(company, data={'dividendes_percent': -1}, partial=True)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_update_dividendes_percent_high_fluctuation(self):
        company = Company.objects.get(id=1)
        serializer = CompanyUpdateSerializer(company, data={'dividendes_percent': 15}, partial=True)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_update_dividendes_percent_too_high(self):
        company = Company.objects.get(id=1)
        serializer = CompanyUpdateSerializer(company, data={'dividendes_percent': 60}, partial=True)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()


@pytest.mark.django_db
class CompanyCreateSerializerTestCase(TestCase):
    def test_valid_data(self):
        valid_data = {
            'type': 1,
            'ticker': 'TICKO',
            'name': 'Test Company',
            'shares_amount': 1000,
            'preferred_shares_amount': 500,
            'dividendes_percent': 5
        }

        serializer = CompanyCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, valid_data)

    def test_invalid_ticker_too_short(self):
        with self.assertRaises(ValidationError):
            CompanyCreateSerializer.validate_ticker('T')

    def test_invalid_ticker_too_long(self):
        with self.assertRaises(ValidationError):
            CompanyCreateSerializer.validate_ticker('TICKOTICKO')

    def test_invalid_shares_amount(self):
        with self.assertRaises(ValidationError):
            CompanyCreateSerializer.validate_shares_amount(0)

    def test_invalid_preferred_shares_amount(self):
        with self.assertRaises(ValidationError):
            CompanyCreateSerializer.validate_preferred_shares_amount(0)

    def test_invalid_dividendes_percent(self):
        with self.assertRaises(ValidationError):
            CompanyCreateSerializer.validate_dividendes_percent(1)


@pytest.mark.django_db
class GoldAmountSerializerTestCase(TestCase):
    def test_valid_amount(self):
        try:
            GoldAmountSerializer.validate_amount(value=10)
        except ValidationError:
            self.fail("validate_amount raised ValidationError unexpectedly")

    def test_invalid_amount(self):
        with self.assertRaises(ValidationError):
            GoldAmountSerializer.validate_amount(value=0)


@pytest.mark.django_db
class ProductsTradingSerializerTestCase(TestCase):
    def test_valid_amount(self):
        try:
            ProductsTradingSerializer.validate_amount(value=10)
        except ValidationError:
            self.fail("validate_amount raised ValidationError unexpectedly")

    def test_invalid_amount(self):
        with self.assertRaises(ValidationError):
            ProductsTradingSerializer.validate_amount(value=0)

    def test_valid_ticker(self):  # existence check
        try:
            ProductsTradingSerializer.validate_ticker('TBMC')
        except ValidationError:
            self.fail("validate_ticker raised ValidationError unexpectedly")

    def test_invalid_ticker(self): # existence check
        with self.assertRaises(ValidationError):
            ProductsTradingSerializer.validate_ticker('LAKE')


class CompanyTransmutationSerializerTestCase(TestCase):
    def test_valid_amount(self):
        try:
            CompanyTransmutationSerializer.validate_dividendes_percent(value=5)
        except ValidationError:
            self.fail("validate_amount raised ValidationError unexpectedly")

    def test_invalid_amount(self):
        with self.assertRaises(ValidationError):
            CompanyTransmutationSerializer.validate_dividendes_percent(value=1)
