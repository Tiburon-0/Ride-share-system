from payment_method import CreditCardPayment, DigitalWalletPayment
from exceptions import BillingError, PaymentError


class BillingInfo:
    
    def __init__(self, user):
        self._user = user
        self._default_method = None
        self._payment_methods = []

    def __str__(self):
        
        ''' User-friendly display for BillingINfo class'''

        if self._default_method is not None:
            return f"{self._user} | {self._default_method}"
        
        else:
            return f"{self._user}"

    def add_payment_method(self, payment_method):

        '''Adds to list of payment methods and checks that '''

        if payment_method is None:
            raise BillingError(f"At least one payment_method is required.")

        if len(self._payment_methods) < 1:
            self._default_method = payment_method

        self._payment_methods.append(payment_method)

        return self._payment_methods

    def set_default_method(self, payment_method):

        '''Updates default method'''

        if payment_method is None:
            raise BillingError("Default payment method cannot be 'None'")

        if payment_method not in self._payment_methods:
            raise BillingError(
                f"Default payment method must be one of the existing payment methods.")
        
        self._default_method = payment_method

        print(f"Default payment method set to {self._default_method}")

        return self._default_method

    def charge_default_payment_method(self, fare, destination):

        '''Calls payment methods and returns ride summary'''

        if self._default_method is None:
            raise BillingError(f"There is no default payment method set.")
        
        if fare <= 0:
            raise PaymentError(f"Fare must be a positive amount. Fare amount triggering error: {fare}")
        
        else:
            amount_charged = self._default_method.charge(fare)
            summary = self._default_method.get_summary(fare, destination)
            print(f"---[Here is your payment summary]---\n{summary}")
            return amount_charged
