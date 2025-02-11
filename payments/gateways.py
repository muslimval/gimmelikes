# payments/gateways.py

import requests
from abc import ABC, abstractmethod
from django.conf import settings
import cryptocompare
from web3 import Web3

class PaymentGateway(ABC):
    @abstractmethod
    def initialize_payment(self, amount, currency, reference):
        pass
    
    @abstractmethod
    def verify_payment(self, reference):
        pass

class OrangeMoneyGateway(PaymentGateway):
    def __init__(self):
        self.api_key = settings.ORANGE_MONEY_API_KEY
        self.base_url = "https://api.orange.com/orange-money-webpay/dev/v1"
        
    def initialize_payment(self, amount, currency, reference):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "merchant_key": settings.ORANGE_MONEY_MERCHANT_KEY,
            "currency": currency,
            "order_id": reference,
            "amount": str(amount),
            "return_url": settings.PAYMENT_RETURN_URL,
            "cancel_url": settings.PAYMENT_CANCEL_URL,
            "notif_url": settings.PAYMENT_NOTIFICATION_URL
        }
        
        response = requests.post(
            f"{self.base_url}/webpayment",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        raise PaymentError("Failed to initialize Orange Money payment")
    
    def verify_payment(self, reference):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{self.base_url}/transactionstatus/{reference}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()["status"] == "SUCCESSFUL"
        return False

class AfrimoneyGateway(PaymentGateway):
    def __init__(self):
        self.api_key = settings.AFRIMONEY_API_KEY
        self.base_url = "https://api.afrimoney.com/v1"
        
    def initialize_payment(self, amount, currency, reference):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": amount,
            "currency": currency,
            "reference": reference,
            "callback_url": settings.PAYMENT_CALLBACK_URL,
            "return_url": settings.PAYMENT_RETURN_URL
        }
        
        response = requests.post(
            f"{self.base_url}/payments",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        raise PaymentError("Failed to initialize Afrimoney payment")
    
    def verify_payment(self, reference):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{self.base_url}/payments/{reference}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()["status"] == "completed"
        return False

class CryptoGateway(PaymentGateway):
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
        self.contract_address = settings.PAYMENT_CONTRACT_ADDRESS
        self.contract_abi = settings.PAYMENT_CONTRACT_ABI
        
    def initialize_payment(self, amount, currency, reference):
        # Get current crypto price
        price = cryptocompare.get_price(currency, 'USD')[currency]['USD']
        crypto_amount = amount / price
        
        # Generate payment address
        payment_address = self.w3.eth.account.create()
        
        return {
            'address': payment_address.address,
            'amount': crypto_amount,
            'currency': currency,
            'reference': reference
        }
    
    def verify_payment(self, reference):
        # Check blockchain for transaction
        contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
        try:
            payment_status = contract.functions.getPaymentStatus(reference).call()
            return payment_status == 1  # 1 = completed
        except Exception as e:
            return False

class PaymentError(Exception):
    pass