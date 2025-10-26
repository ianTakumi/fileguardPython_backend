from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-t%hrwlsp1re$f-%i4wr+$st7(r*7lc%-r54h-l@6&x(cq!c0!d')

DEBUG = True

ALLOWED_HOSTS = ['*']  # Allow all during development

# ---------------------------------------------------------------------
# 🧩 INSTALLED APPS
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party
    'rest_framework',
    'corsheaders',

    # Local Apps
    'AppUser',
    'files',
    'contacts'
]

# ---------------------------------------------------------------------
# 🧠 MIDDLEWARE
# ---------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------
# 🗄️ DATABASE (you’ll use Supabase via supabase-py, so keep sqlite for now)
# ---------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('SUPABASE_DB_HOST'),
        'PORT': os.getenv('SUPABASE_PORT'),
        'NAME': os.getenv('SUPABASE_DB_NAME'),
        'USER': os.getenv('SUPABASE_DB_USER'),
        'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD'),
        'OPTIONS': {'sslmode': 'require'},  # important for Supabase
    }
}
# ---------------------------------------------------------------------
# 🔐 AUTHENTICATION
# ---------------------------------------------------------------------
AUTH_USER_MODEL = 'auth.User'

# ---------------------------------------------------------------------
# 🌍 CORS (allow frontend to call API)
# ---------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------
# 🕒 TIME & LANGUAGE
# ---------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# 📁 STATIC FILES
# ---------------------------------------------------------------------
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------
# 🪣 SUPABASE CONFIG
# ---------------------------------------------------------------------
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
SUPABASE_DB_NAME = os.getenv('SUPABASE_DB_NAME', '')
SUPABASE_DB_USER = os.getenv('SUPABASE_DB_USER', '')
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '')
SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST', '')
SUPABASE_PORT = os.getenv('SUPABASE_PORT', '5432')
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL", "https://xyzcompanyabc.supabase.co")
