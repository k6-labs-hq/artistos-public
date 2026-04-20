"""Currency validation using ISO 4217 standards.

Issue #77: Enforce ISO 4217 3-letter currency codes on all claim creation endpoints.
"""

from typing import Set

# ISO 4217 currency codes
# https://en.wikipedia.org/wiki/ISO_4217
ISO_4217_CODES: Set[str] = {
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD",
    "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK",
    "DJF", "DKK", "DOP", "DZD",
    "EGP", "ERN", "ETB", "EUR",
    "FJD", "FKP",
    "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD",
    "HKD", "HNL", "HRK", "HTG", "HUF",
    "IDR", "ILS", "INR", "IQD", "IRR", "ISK",
    "JMD", "JOD", "JPY",
    "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT",
    "LAK", "LBP", "LKR", "LRD", "LSL", "LYD",
    "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN",
    "NAD", "NGN", "NIO", "NOK", "NPR", "NZD",
    "OMR",
    "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG",
    "QAR",
    "RON", "RSD", "RUB", "RWF",
    "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SPL", "SRD", "STN", "SYP", "SZL",
    "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TVD", "TWD", "TZS",
    "UAH", "UGX", "USD", "USN", "UYI", "UYU", "UYW", "UZS",
    "VED", "VES", "VND", "VUV",
    "WST",
    "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX",
    "YER",
    "ZAR", "ZMW", "ZWL",
}


class InvalidCurrencyError(ValueError):
    """Raised when an invalid currency code is provided."""
    
    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        super().__init__(
            f"Invalid currency code: '{currency_code}'. "
            f"Must be a valid ISO 4217 3-letter code (e.g., USD, EUR, GBP)."
        )


def validate_currency_code(currency_code: str | None) -> str:
    """
    Validate that a currency code conforms to ISO 4217 standards.
    
    Args:
        currency_code: 3-letter currency code (e.g., "USD", "EUR")
        
    Returns:
        Uppercase currency code if valid
        
    Raises:
        InvalidCurrencyError: If currency code is not in ISO 4217
        ValueError: If currency code is None or empty
        
    Example:
        >>> validate_currency_code("usd")
        "USD"
        >>> validate_currency_code("FAKE")
        InvalidCurrencyError: Invalid currency code: 'FAKE'
    """
    if not currency_code:
        raise ValueError("Currency code cannot be None or empty")
    
    normalized = currency_code.strip().upper()
    
    if normalized not in ISO_4217_CODES:
        raise InvalidCurrencyError(normalized)
    
    return normalized


def is_valid_currency_code(currency_code: str | None) -> bool:
    """
    Check if a currency code is valid without raising an exception.
    
    Args:
        currency_code: 3-letter currency code to check
        
    Returns:
        True if valid ISO 4217 code, False otherwise
        
    Example:
        >>> is_valid_currency_code("USD")
        True
        >>> is_valid_currency_code("FAKE")
        False
    """
    if not currency_code:
        return False
    
    return currency_code.strip().upper() in ISO_4217_CODES
