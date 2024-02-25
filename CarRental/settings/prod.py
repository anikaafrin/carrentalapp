from .base import *

DEBUG = False

ALLOWED_HOSTS = ['car-rental-rest-api.herokuapp.com',
                '127.0.0.1']


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd24gp8j7ufs7qq',
        'USER': 'ghfykijucmbmfa',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'ec2-34-255-134-200.eu-west-1.compute.amazonaws.com',
        'PORT': '5432',
    }
}

# AWS S3 credentials


AWS_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'api-car-rental'

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_HOST = "s3.eu-central-1.amazonaws.com" 
AWS_S3_REGION_NAME="eu-central-1"

AWS_QUERYSTRING_AUTH = False