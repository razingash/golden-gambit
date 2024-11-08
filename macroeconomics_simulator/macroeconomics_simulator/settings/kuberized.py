from .base import *

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://redis.backend-services.svc.cluster.local:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_BROKER_URL = "amqp://admin:admin@rabbitmq.backend-services.svc.cluster.local:5672//"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis.backend-services.svc.cluster.local', 6379)],
            "capacity": 1000,
            "expiry": 10,
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'macroeconomics_simulator'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'root'),
        'HOST': 'postgres.backend-services.svc.cluster.local',
        'PORT': '5432',
    }
}
