"""
Categorical variables uses in the app schemas
"""

import enum


class PaymentMethodType(str, enum.Enum):
    cash = "Cash"
    paypal = "Paypal"
    bank_transfer = "Bank Transfer"


class CurrencyType(str, enum.Enum):
    euro = "EURO"
    usd = "USD"


class CategoryType(str, enum.Enum):
    minijob = "Minijob"
    freelance = "Freelance"
    commission = "Commission"
    expenses = "Expenses"


class FrequencyType(str, enum.Enum):
    weekly = "Weekly"
    monthly = "Monthly"
    quarterly = "Quarterly"
    biannually = "Biannually"
    yearly = "Yearly"
    one_time = "One Time"
