from django.urls import reverse
from rest_framework.test import APITestCase


class RegistrationUrlTestCase(APITestCase):
    def test_url(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class TokenObtainPairViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('token_obtain_pair')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class TokenRefreshViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('token_refresh')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class TokenVerifyWithBlacklistViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('token_verify')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class LogoutViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)


class UserApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('user_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)


class UserCompaniesViewTestCase(APITestCase):
    def test_url_get(self):
        url = reverse('user_companies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_url_post(self):
        url = reverse('user_companies')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)


class UserSharesViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('user_shares')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)


class CompanyListViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('companies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class CompanyRecipesTestCase(APITestCase):
    def test_url_get(self):
        url = reverse('companies-recipes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_url_post(self):
        url = reverse('companies-recipes')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)


class CompanyApiViewTestCase(APITestCase):
    def test_url_get(self):
        url = reverse('company', kwargs={'ticker': 'TBMC'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_patch(self):
        url = reverse('company', kwargs={'ticker': 'TBMC'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)


class CompanyWarehouseApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('company_warehouse', kwargs={'ticker': 'TBMC'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)


class CompanyWarehouseUpdateApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('company_warehouse_update', kwargs={'ticker': 'TBMC'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)


class CompanyPrintNewSharesApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('company_print_shares', kwargs={'ticker': 'TBMC'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)


class CompanySellShareApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('company_sell_shares', kwargs={'ticker': 'TBMC'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)


class CompanyHistoryApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('company_history', kwargs={'ticker': 'TBMC'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StockGoldApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('gold_to_silver_price')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StockGoldHistoryApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('gold_to_silver_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class GoldExchangeApiViewTestCase(APITestCase):
    def test_url_purchase(self):
        url = reverse('gold-exchange', kwargs={'transaction_type': 'buy'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_url_sale(self):
        url = reverse('gold-exchange', kwargs={'transaction_type': 'sell'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)


class StockProductsApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('products-pricing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ProductsExchangeApiViewTestCase(APITestCase):
    def test_url_purchase(self):
        url = reverse('products-exchange', kwargs={'transaction_type': 'buy'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_url_sale(self):
        url = reverse('products-exchange', kwargs={'transaction_type': 'sell'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)


class SharesWholesaleListApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('shares-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SharesExchangeApiViewTestCase(APITestCase):
    def test_url_get(self):
        url = reverse('shares-exchange', kwargs={'ticker': 'TBMC'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_post(self):
        url = reverse('shares-exchange', kwargs={'ticker': 'TBMC'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)


class SharesExchangeWholesaleApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('shares-exchange-wholesale', kwargs={'ticker': 'TBMC'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)


class LawsApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('laws')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class EventsApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('events')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TopCompaniesApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('top-companies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TopUsersApiViewTestCase(APITestCase):
    def test_url(self):
        url = reverse('top-users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ActualGoldPriceSseStreamTestCase(APITestCase):
    def test_sse_stream_url(self):
        url = reverse('gold_to_silver_actual_price')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
