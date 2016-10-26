import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '28ta%!1(r3z17!xq4nh6-5!u_s-v37z!f#0!zt)jy61zwp4)a9'

DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['127.0.0.1']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'driving.urls'

WSGI_APPLICATION = 'driving.wsgi.application'

# Database
if 'SERVER_SOFTWARE' in os.environ:
    from sae.const import (
        MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
else:
    MYSQL_HOST = '120.25.124.178'
    MYSQL_PORT = '3306'
    MYSQL_USER = 'root'
    MYSQL_PASS = '123123'
    MYSQL_DB = 'app_driverdemo'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_DB,
        'USER': MYSQL_USER,
        'PASSWORD': MYSQL_PASS,
        'HOST': MYSQL_HOST,
        'PORT': MYSQL_PORT,
    }
}

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/assets/'
STATIC_ROOT = os.path.join(BASE_DIR, 'assets/').replace('\\', '/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "app/assets/").replace('\\', '/'),
    os.path.join(BASE_DIR, "admin/assets/").replace('\\', '/'),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates/").replace('\\', '/'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': dict(standard={
#         'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}),
#     'filters': {
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'include_html': True,
#         },
#         'default': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(STATIC_ROOT + '/logs/', 'all.log'),
#             'maxBytes': 1024 * 1024 * 5,
#             'backupCount': 5,
#             'formatter': 'standard',
#         },
#         'error': {
#             'level': 'ERROR',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(STATIC_ROOT + '/logs/', 'error.log'),
#             'maxBytes': 1024 * 1024 * 5,
#             'backupCount': 5,
#             'formatter': 'standard',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard'
#         },
#         'request_handler': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(STATIC_ROOT + '/logs/', 'script.log'),
#             'maxBytes': 1024 * 1024 * 5,
#             'backupCount': 5,
#             'formatter': 'standard',
#         },
#         'scprits_handler': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(STATIC_ROOT + '/logs/', 'script.log'),
#             'maxBytes': 1024 * 1024 * 5,
#             'backupCount': 5,
#             'formatter': 'standard',
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['default', 'console'],
#             'level': 'DEBUG',
#             'propagate': False
#         },
#         'django.request': {
#             'handlers': ['request_handler'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#         'scripts': {
#             'handlers': ['scprits_handler'],
#             'level': 'INFO',
#             'propagate': False
#         },
#         'admin.views': {
#             'handlers': ['default', 'error'],
#             'level': 'DEBUG',
#             'propagate': True
#         },
#         'app.views': {
#             'handlers': ['error'],
#             'level': 'ERROR',
#             'propagate': True
#         }
#     }
# }
#
#
#


# TEMPLATE zh_CN
FILE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'

AUTH_USER_MODEL = 'app.User'

# SMS Info
SMSGLOBAL_USERNAME = '6SDK-EMY-6688-KKTLN'
SMSGLOBAL_PASSWORD = '273442'
SMSGLOBAL_API_URL_SENDSMS = 'http://sdk4report.eucp.b2m.cn:8080/sdkproxy/sendsms.action'
SMSGLOBAL_API_URL_CHECKBALANCE = 'http://sdk4report.eucp.b2m.cn:8080/sdkproxy/querybalance.action'