import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-this'
    
    # SQLite Database Configuration (for development)
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = bool(os.environ.get('SESSION_COOKIE_SECURE', '0') == '1')
    
    # SQLite specific settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }

    # Admin login restriction
    ADMIN_LOGIN_EMAIL = os.environ.get('ADMIN_LOGIN_EMAIL') or 'satellite@gmail.ac.tz'
    ADMIN_LOGIN_PASSWORD = os.environ.get('ADMIN_LOGIN_PASSWORD') or 'admin123'

    # LIPA NAMBA (Till Number) configuration - defaults for application fee page
    LIPA_NAMBA_TILL = os.environ.get('LIPA_NAMBA_TILL') or '000000'
    LIPA_NAMBA_NAME = os.environ.get('LIPA_NAMBA_NAME') or 'SATELLITE PRE & PRIMARY SCHOOL'
    APPLICATION_FEE_AMOUNT = float(os.environ.get('APPLICATION_FEE_AMOUNT') or 10000)
    APPLICATION_LIPA_NAMBAS = [
        {"till": os.environ.get('APP_TILL_1', '000000'), "name": os.environ.get('APP_NAME_1', 'SATELLITE APPLICATIONS'), "amount": float(os.environ.get('APPLICATION_FEE_AMOUNT', 10000))},
        {"till": os.environ.get('APP_TILL_2', '000001'), "name": os.environ.get('APP_NAME_2', 'SATELLITE APPLICATIONS ALT'), "amount": float(os.environ.get('APPLICATION_FEE_AMOUNT', 10000))},
    ]

    # Multiple LIPA NAMBA sets per payment category
    FEES_LIPA_NAMBAS = [
        {"till": os.environ.get('FEES_TILL_1', '111111'), "name": os.environ.get('FEES_NAME_1', 'SATELLITE FEES'), "amount": float(os.environ.get('FEES_AMOUNT', 150000))},
        {"till": os.environ.get('FEES_TILL_2', '111112'), "name": os.environ.get('FEES_NAME_2', 'SATELLITE FEES ALT'), "amount": float(os.environ.get('FEES_AMOUNT_ALT', 150000))},
    ]
    MEALS_LIPA_NAMBAS = [
        {"till": os.environ.get('MEALS_TILL_1', '222221'), "name": os.environ.get('MEALS_NAME_1', 'SATELLITE MEALS'), "amount": float(os.environ.get('MEALS_AMOUNT', 50000))},
        {"till": os.environ.get('MEALS_TILL_2', '222222'), "name": os.environ.get('MEALS_NAME_2', 'SATELLITE MEALS ALT'), "amount": float(os.environ.get('MEALS_AMOUNT_ALT', 50000))},
    ]
    TRANSPORT_LIPA_NAMBAS = [
        {"till": os.environ.get('TRANSPORT_TILL_1', '333331'), "name": os.environ.get('TRANSPORT_NAME_1', 'SATELLITE TRANSPORT'), "amount": float(os.environ.get('TRANSPORT_AMOUNT', 80000))},
        {"till": os.environ.get('TRANSPORT_TILL_2', '333332'), "name": os.environ.get('TRANSPORT_NAME_2', 'SATELLITE TRANSPORT ALT'), "amount": float(os.environ.get('TRANSPORT_AMOUNT_ALT', 80000))},
    ]