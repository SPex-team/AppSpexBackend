"""
Django settings for AppSpexBackend project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from . import project_env

ENV = project_env.ENV

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9=)nx*#m+2q0)#+@v%d2ue9gwjfxdw^vx$djo%^4g=l76feee0'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',
    'devops_django',
    'spex',
    'c_test',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AppSpexBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AppSpexBackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'spex',
        'USER': 'root',
        'PASSWORD': 'wonders,1',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = ["http://192.168.19.27:3001"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'token',
)

SESSION_COOKIE_AGE = 86400 * 7

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'devops_django.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'devops_django.paginations.StandardResultsSetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    )
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
            # 日志格式
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'prom': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/prom.log',
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'spex': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/spex.log',
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'tasks': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/tasks.log',
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db': {
            'handlers': ['console'] if ENV != "PRO" else [],
            'level': 'DEBUG',
            'propagate': False,
        },
        'prom': {
            'handlers': ['prom'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'spex': {
            'handlers': ['spex'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tasks': {
            'handlers': ['tasks'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}


CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CELERY_BROKER_URL = "amqp://alert:alert,1@192.168.1.128/alert"
CELERY_RESULT_BACKEND = "django-db"


STATIC_URL = '/django-static/'
STATIC_ROOT = os.path.join(BASE_DIR, "django-static")

CONTRACT_ABI_STR = '[{"inputs":[],"name":"AccountAlreadyEnabled","type":"error"},{"inputs":[],"name":"ApprovalNotWithinTimeframe","type":"error"},{"inputs":[],"name":"BelowMinimumBlockPeriod","type":"error"},{"inputs":[],"name":"BurnRatePositive","type":"error"},{"inputs":[],"name":"CallerNotOperatorOwner","type":"error"},{"inputs":[],"name":"CallerNotValidatorOwner","type":"error"},{"inputs":[],"name":"ExceedManagingOperatorsPerAccountLimit","type":"error"},{"inputs":[],"name":"FeeExceedsIncreaseLimit","type":"error"},{"inputs":[],"name":"FeeTooLow","type":"error"},{"inputs":[],"name":"NegativeBalance","type":"error"},{"inputs":[],"name":"NoPendingFeeChangeRequest","type":"error"},{"inputs":[],"name":"NotEnoughBalance","type":"error"},{"inputs":[],"name":"OperatorWithPublicKeyNotExist","type":"error"},{"inputs":[],"name":"ValidatorWithPublicKeyNotExist","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"}],"name":"AccountEnable","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"}],"name":"AccountLiquidation","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"DeclareOperatorFeePeriodUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":false,"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"DeclaredOperatorFeeCancelation","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"ExecuteOperatorFeePeriodUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":true,"internalType":"address","name":"senderAddress","type":"address"}],"name":"FundsDeposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"}],"name":"FundsWithdrawal","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"LiquidationThresholdPeriodUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"MinimumBlocksBeforeLiquidationUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"oldFee","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newFee","type":"uint256"}],"name":"NetworkFeeUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":false,"internalType":"address","name":"recipient","type":"address"}],"name":"NetworkFeesWithdrawal","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":false,"internalType":"uint32","name":"operatorId","type":"uint32"},{"indexed":false,"internalType":"uint256","name":"blockNumber","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"OperatorFeeDeclaration","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":false,"internalType":"uint32","name":"operatorId","type":"uint32"},{"indexed":false,"internalType":"uint256","name":"blockNumber","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"OperatorFeeExecution","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"OperatorFeeIncreaseLimitUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"OperatorMaxFeeIncreaseUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"id","type":"uint32"},{"indexed":false,"internalType":"string","name":"name","type":"string"},{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":false,"internalType":"bytes","name":"publicKey","type":"bytes"},{"indexed":false,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"OperatorRegistration","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"operatorId","type":"uint32"},{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"}],"name":"OperatorRemoval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"operatorId","type":"uint32"},{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":false,"internalType":"uint256","name":"blockNumber","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"score","type":"uint256"}],"name":"OperatorScoreUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"RegisteredOperatorsPerAccountLimitUpdate","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":false,"internalType":"bytes","name":"publicKey","type":"bytes"},{"indexed":false,"internalType":"uint32[]","name":"operatorIds","type":"uint32[]"},{"indexed":false,"internalType":"bytes[]","name":"sharesPublicKeys","type":"bytes[]"},{"indexed":false,"internalType":"bytes[]","name":"encryptedKeys","type":"bytes[]"}],"name":"ValidatorRegistration","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"ownerAddress","type":"address"},{"indexed":false,"internalType":"bytes","name":"publicKey","type":"bytes"}],"name":"ValidatorRemoval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"ValidatorsPerOperatorLimitUpdate","type":"event"},{"inputs":[{"internalType":"address","name":"ownerAddress","type":"address"}],"name":"addressNetworkFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"cancelDeclaredOperatorFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"},{"internalType":"uint256","name":"operatorFee","type":"uint256"}],"name":"declareOperatorFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"ownerAddress","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"executeOperatorFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"ownerAddress","type":"address"}],"name":"getAddressBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"ownerAddress","type":"address"}],"name":"getAddressBurnRate","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getDeclaredOperatorFeePeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getExecuteOperatorFeePeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getLiquidationThresholdPeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getNetworkEarnings","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getNetworkFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"getOperatorById","outputs":[{"internalType":"string","name":"","type":"string"},{"internalType":"address","name":"","type":"address"},{"internalType":"bytes","name":"","type":"bytes"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"}],"name":"getOperatorByPublicKey","outputs":[{"internalType":"string","name":"","type":"string"},{"internalType":"address","name":"","type":"address"},{"internalType":"bytes","name":"","type":"bytes"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"getOperatorDeclaredFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"getOperatorFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getOperatorFeeIncreaseLimit","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"}],"name":"getOperatorsByValidator","outputs":[{"internalType":"uint32[]","name":"","type":"uint32[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"ownerAddress","type":"address"}],"name":"getValidatorsByOwnerAddress","outputs":[{"internalType":"bytes[]","name":"","type":"bytes[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract ISSVRegistry","name":"registryAddress_","type":"address"},{"internalType":"contract IERC20","name":"token_","type":"address"},{"internalType":"uint64","name":"minimumBlocksBeforeLiquidation_","type":"uint64"},{"internalType":"uint64","name":"operatorMaxFeeIncrease_","type":"uint64"},{"internalType":"uint64","name":"declareOperatorFeePeriod_","type":"uint64"},{"internalType":"uint64","name":"executeOperatorFeePeriod_","type":"uint64"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"ownerAddress","type":"address"}],"name":"isLiquidatable","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"ownerAddress","type":"address"}],"name":"isLiquidated","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"ownerAddresses","type":"address[]"}],"name":"liquidate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"reactivateAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"bytes","name":"publicKey","type":"bytes"},{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"registerOperator","outputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"},{"internalType":"uint32[]","name":"operatorIds","type":"uint32[]"},{"internalType":"bytes[]","name":"sharesPublicKeys","type":"bytes[]"},{"internalType":"bytes[]","name":"sharesEncrypted","type":"bytes[]"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"registerValidator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"removeOperator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"}],"name":"removeValidator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"newDeclareOperatorFeePeriod","type":"uint64"}],"name":"updateDeclareOperatorFeePeriod","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"newExecuteOperatorFeePeriod","type":"uint64"}],"name":"updateExecuteOperatorFeePeriod","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"blocks","type":"uint64"}],"name":"updateLiquidationThresholdPeriod","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"updateNetworkFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"newOperatorMaxFeeIncrease","type":"uint64"}],"name":"updateOperatorFeeIncreaseLimit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"},{"internalType":"uint32","name":"score","type":"uint32"}],"name":"updateOperatorScore","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"},{"internalType":"uint32[]","name":"operatorIds","type":"uint32[]"},{"internalType":"bytes[]","name":"sharesPublicKeys","type":"bytes[]"},{"internalType":"bytes[]","name":"sharesEncrypted","type":"bytes[]"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"updateValidator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"operatorId","type":"uint32"}],"name":"validatorsPerOperatorCount","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"withdrawAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdrawNetworkEarnings","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
CONTRACT_ADDRESS = "0xb9e155e65B5c4D66df28Da8E9a0957f06F11Bc04"
ETHEREUM_HTTP_PROVIDER = "http://39.101.73.37:8545"

