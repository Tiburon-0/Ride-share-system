from exceptions import PaymentError

class PaymentMethod:

    def __init__(self, owner_name, method_id):
        self._owner_name = owner_name
        self._method_id = method_id

    def __str__(self):
        '''User-friendly display for PaymentMethod class'''
        return f"{self._owner_name} {self._method_id}"

    # Getter methods

    def get_owner_name(self):
        '''Returns owner of payment method'''
        return self._owner_name

    def get_method_id(self):
        '''Returns payment method id'''
        return self._method_id

    # Service methods

    def charge(self, fare):
        '''Charges rider based on the specified fare'''
        return f"Charge: ${fare}."

    def get_summary(self, fare, ride):
        '''Returns transaction summary'''
        return f"You have been charged ${fare} for your trip: {ride}."


class CreditCardPayment(PaymentMethod):

    def __init__(self, method_id, owner_name, card_number, expiration_date, billing_address):

        super().__init__(owner_name, method_id)
        self._card_number = card_number
        self._expiration_date = expiration_date
        self._billing_address = billing_address

    def __str__(self):
        return f"{self._owner_name} | {self._card_number}, {self._expiration_date}"

    # Getter methods

    def get_card_number(self):
        '''Returns CreditCard number'''
        return self._card_number

    def get_expiration_date(self):
        '''Returns CreditCard expiration date'''
        return self._expiration_date

    def get_billing_address(self):
        '''Returns CreditCard billing address'''
        return self._billing_address

    # Setter methods

    def set_card_number(self, card_number):
        '''Updates card number'''
        self._card_number = card_number
        return self._card_number

    def set_billing_address(self, billing_address):
        '''Updates billing address'''
        self._billing_address = billing_address
        return self._billing_address

    def set_expiration_date(self, expiration_date):
        '''Updates expiration date'''
        self._expiration_date = expiration_date
        return self._expiration_date

    # Service methods

    def charge(self, fare):
        '''Charges rider based on the specified fare'''
        # Handles invalid fare amount
        if fare <= 0:
            raise PaymentError(f"Fare amount must be positive. Fare amount triggering error: {fare}")
        
        # Handles expired card
        if self._expiration_date < "12/27":
            raise PaymentError(f"Card expired...Card expiration date: {self._expiration_date}")
    
        # Simulates decline for invalid card number
        if str(self._card_number).endswith("0000"):
            raise PaymentError(f"Payment declined...Invalid card number: {self._card_number}")
        
        return f"Your CreditCard has been charged: ${fare}."

    def get_summary(self, fare, destination):
        '''Returns payment, fare amount, and destination'''
        return f"Your CreditCard has been charged ${fare} for your trip to {destination}."

class DigitalWalletPayment(PaymentMethod):

    def __init__(self, method_id, owner_name, wallet_provider, wallet_id):

        super().__init__(owner_name, method_id)
        self._wallet_provider = wallet_provider
        self._wallet_id = wallet_id

    def __str__(self):
        return f"{self._owner_name} | {self._wallet_provider}, {self._wallet_id}"

    # Getter methods

    def get_wallet_provider(self):
        '''Returns wallet provider'''
        return self._wallet_provider

    def get_wallet_id(self):
        '''Returns wallet id'''
        return self._wallet_id

    # Setter methods

    def set_wallet_provider(self, wallet_provider):
        '''Updates wallet provider'''
        self._wallet_provider = wallet_provider
        return self._wallet_provider

    def set_wallet_id(self, wallet_id):
        '''Updates wallet id'''
        self._wallet_id = wallet_id
        return self._wallet_id

    # Service methods

    def charge(self, fare):
        '''Processes the payment'''
        # Handles invalid fare amount
        if fare <= 0:
            raise PaymentError(f"Fare amount must be positive. Fare amount triggering error: {fare}")
        
        # Handles expired card
        valid_wallet_providers = ["Google", "Apple"]
        if self._wallet_provider not in valid_wallet_providers:
            raise PaymentError(f"Unsupported wallet_provider passed: {self._wallet_provider}")

        if self._wallet_id is None:
            raise PaymentError(f"Wallet_id has not been set")
        
        if "blocked" in str(self._wallet_id).lower():
            raise PaymentError(f"Payment method with wallet_id: {self._wallet_id} is blocked.")

        return f"Your Digital Wallet has been charged: ${fare}."

    def get_summary(self, fare, destination):
        '''Returns payment, fare amount, and destination'''
        return f"Your Digital Wallet has been charged ${fare} for your trip to {destination}."
