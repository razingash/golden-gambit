from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

import datetime

from stock.models import Company, PlayerCompanies, SharesExchange
from stock.utils.exceptions import custom_logger


class BaseTestCase(APITestCase): # used to authenticated users
    def setUp(self):
        self.user = get_user_model().objects.get(username='djangobot1')
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)
        self.url = None

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.refresh.access_token))


class RegisterViewPermissionTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_valid_post(self):
        data = {
            'username': 'testbotRegister',
            'password': 'testbot_Register'
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_post(self):
        data = {
            'username': 'test',
            'password': 'testbot_register'
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)


class LogoutViewPermissionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('logout')

    def test_logout_authenticated_user(self):
        self.authenticate()
        response = self.client.post(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_non_authenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenVerifyWithBlacklistViewTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.get(username='djangobot1')
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh_token.access_token)
        self.blacklist_url = reverse('token_verify')

    def test_verify_valid_token(self):
        response = self.client.post(self.blacklist_url, data={'token': str(self.access_token)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_blacklisted_token(self):
        outstanding_token = OutstandingToken.objects.get(token=self.refresh_token)
        BlacklistedToken.objects.create(token=outstanding_token)
        response = self.client.post(self.blacklist_url, data={'token': str(self.refresh_token)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('user_info')

    def test_authenticated_user(self):
        self.authenticate()
        response = self.client.get(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserCompaniesViewPermissionTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testbot3', password='testbot3')
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)
        self.url = reverse('user_companies')

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.refresh.access_token))

    def test_authenticated_user(self):
        self.authenticate()
        response = self.client.get(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post(self): # register company
        valid_data = {
            'type': 1,
            'ticker': 'TEST3',
            'name': 'Test Company3',
            'shares_amount': 1000,
            'preferred_shares_amount': 500,
            'dividendes_percent': 5
        }
        self.authenticate()
        response = self.client.post(self.url, data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserSharesViewPermissionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('user_shares')

    def test_authenticated_user(self): # get
        self.authenticate()
        response = self.client.get(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_authenticated_user(self): # get
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CompanyRecipesPermissionTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testbot4', password='testbot4')
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)
        self.url = reverse('user_companies')

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.refresh.access_token))

    def test_authenticated_user(self): # get
        self.authenticate()
        response = self.client.get(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_authenticated_user(self): # get
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    """
    def test_post(self):
        valid_data_1 = {
            'type_id': 1,
            'ticker': 'TEST40',
            'name': 'Test Company40',
            'shares_amount': 1000,
            'preferred_shares_amount': 500,
            'dividendes_percent': 5
        }
        valid_data_2 = {
            'type_id': 1,
            'ticker': 'TEST41',
            'name': 'Test Company41',
            'shares_amount': 1000,
            'preferred_shares_amount': 500,
            'dividendes_percent': 5
        }
        post_data = {
            'tickers': ['TEST40', 'TEST41'],
            'recipe_id': 1,
            'name': 'New Merged Company',
            'dividendes_percent': 4.5,
            'ticker': 'MERGED_TICKER'
        }
        self.authenticate()
        company_1 = Company.objects.create(**valid_data_1)
        company_2 = Company.objects.create(**valid_data_2)
        PlayerCompanies.objects.create(player=self.user, company=company_1, shares_amount=1000, preferred_shares_amount=500)
        PlayerCompanies.objects.create(player=self.user, company=company_2, shares_amount=1000, preferred_shares_amount=500)

        response = self.client.post(self.url, data=post_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        merged_company = Company.objects.get(ticker='MERGED_TICKER')
        self.assertIsNotNone(merged_company)
        self.assertEqual(merged_company.name, 'New Merged Company')
        self.assertEqual(merged_company.dividendes_percent, 4.5)
        self.assertEqual(merged_company.ticker, 'MERGED_TICKER')
    """


class CompanyApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('company', kwargs={'ticker': 'TBMC'})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_non_authenticated_user(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_authenticated_user(self):
        self.authenticate()
        response = self.client.patch(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_head(self):
        self.authenticate()
        response = self.client.patch(reverse('company', kwargs={'ticker': 'TBTA'}), data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyWarehouseApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('company_warehouse', kwargs={'ticker': 'TBMC'})

    def test_non_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_head(self):
        self.authenticate()
        response = self.client.get(reverse('company_warehouse', kwargs={'ticker': 'TBTA'}), data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_head(self):
        self.authenticate()
        response = self.client.get(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CompanyPrintNewSharesApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('company_print_shares', kwargs={'ticker': 'TBMC'})

    def test_non_authenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_head_of_company(self):
        valid_data = {
            'shares_type': 1,
            'amount': 100,
            'price': 10
        }
        self.authenticate()
        response = self.client.post(reverse('company_print_shares', kwargs={'ticker': 'TBTA'}), data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_head_of_company(self):
        self.authenticate()
        response = self.client.post(self.url, data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CompanySellShareApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('company_print_shares', kwargs={'ticker': 'TBTA'})

    def test_non_authenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user(self):
        valid_data = {
            'shares_type': 1,
            'amount': 100,
            'price': 10
        }
        self.authenticate()
        response = self.client.post(self.url, data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyHistoryApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('company_history', kwargs={'ticker': 'TBMC'})

    def test_non_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StockGoldApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('gold_to_silver_price')

    def test_non_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GoldExchangeApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('gold-exchange', kwargs={'transaction_type': 'buy'})
        self.valid_data = {'amount': 1}

    def test_non_authenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_purchase_gold(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_sale_gold(self):
        response = self.client.post(reverse('gold-exchange', kwargs={'transaction_type': 'sell'}), data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StockGoldHistoryApiViewTestCase(APITestCase):
    def test_non_authenticated_user(self):
        response = self.client.get(reverse('gold_to_silver_history'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StockProductsApiViewTestCase(APITestCase):
    def test_non_authenticated_user(self):
        response = self.client.get(reverse('products-pricing'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductsExchangeApiView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('products-exchange', kwargs={'transaction_type': 'buy'})
        self.valid_data = {
            'ticker': 'TBTA',
            'amount': 1,
            'type': 1
        }

    def test_non_authenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_purchase_gold(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_sale_gold(self):
        response = self.client.post(reverse('products-exchange', kwargs={'transaction_type': 'sell'}), data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SharesWholesaleListApiViewTestCase(APITestCase):
    def test_non_authenticated_user(self):
        response = self.client.get(reverse('shares-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class SharesExchangeApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('shares-exchange', kwargs={'ticker': 'TBMC'})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_non_authenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_authenticated_user(self):
        company = Company.objects.get(ticker='TBMC')
        pc = PlayerCompanies.objects.select_related('company', 'player').get(company=company)
        timestamp = timezone.now() - datetime.timedelta(days=10)
        lot = SharesExchange.objects.create(player=pc.player, company=company, amount=100, price=10, shares_type=1,
                                            owners_right=timestamp, shareholders_right=timestamp)
        valid_data = {
            'shares_type': 1,
            'amount': 10,
            'price': lot.price,
            'id': lot.id
        }
        self.authenticate()
        response = self.client.post(reverse('shares-exchange', kwargs={'ticker': 'TBMC'}), data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SharesExchangeWholesaleApiViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('shares-exchange-wholesale', kwargs={'ticker': 'TBMC'})

    def test_post_non_authenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_authenticated_user(self):
        company = Company.objects.get(ticker='TBMC')
        pc = PlayerCompanies.objects.select_related('company', 'player').get(company=company)
        timestamp = timezone.now() - datetime.timedelta(days=10)
        SharesExchange.objects.create(player=pc.player, company=company, amount=100, price=10, shares_type=1,
                                      owners_right=timestamp, shareholders_right=timestamp)
        valid_data = {
            'shares_type': 1,
            'reserved_money': 100,
            'desired_quantity': 10,
        }
        self.authenticate()
        response = self.client.post(reverse('shares-exchange-wholesale', kwargs={'ticker': 'TBMC'}), data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LawsApiViewTestCase(APITestCase):
    def test_non_authenticated_user(self):
        response = self.client.get(reverse('laws'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventsApiViewTestCase(APITestCase):
    def test_non_authenticated_user(self):
        response = self.client.get(reverse('events'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TopCompaniesApiViewTestCase(APITestCase):
    def test_non_authenticated_user(self):
        response = self.client.get(reverse('top-companies'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TopUsersApiViewTestCase(APITestCase):
    def test_non_authenticated_user(self):
        response = self.client.get(reverse('top-users'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
