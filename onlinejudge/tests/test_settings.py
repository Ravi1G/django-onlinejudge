SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'onlinejudge',
    'onlinejudge.tests',
    'crispy_forms',
    'sekizai',
    'taggit',
    'django_markup',
    'django_comments',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'onlinejudge.sqlite',
    }
}
ROOT_URLCONF = 'onlinejudge.urls'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
