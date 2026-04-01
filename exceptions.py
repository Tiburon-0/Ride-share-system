class RideHailingError(Exception):
    '''Base class for all custom errors in the ride-hailing system'''
    pass


class DataLoadError(RideHailingError):
    '''Raised when a JSON file cannot be opened or read'''
    pass


class DataFormatError(RideHailingError):
    '''Raised when JSON structure or types are invalid'''
    pass


class DataReferenceError(RideHailingError):
    '''Raised when IDs in JSON refer to missing entities'''
    pass


class BillingError(RideHailingError):
    '''Base class for billing-related errors'''
    pass


class PaymentError(BillingError):
    '''Raised when a payment method cannot successfully charge'''
    pass


class RideLogicError(RideHailingError):
    '''Raised when ride state is inconsistent or incomplete'''
    pass
