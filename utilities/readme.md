# Installation Instructions

1. copy `django/utilites` folder to your project as `django/utilities`
2. Delete the migration folder
3. pip install -r django/utilites/requirements.txt
4. Add the following Installed apps to your settings file

```
    INSTALLED_APPS = [
        #add jet apps at top of list.
        'jet.dashboard',
        'jet',
        ...
        ...
        ...

        # need these for utilities to work
        'phonenumber_field',
        'localflavor',
        'simple_history',
        'django_extensions',
        'import_export',
        'storages',  #### aws s3 storage ###
        'utilities.apps.BaseModelConfig',
        # end of utilites

        ...
        ...
    ]
 ```

5. Add the following middlewares to your settings file

 ```
    MIDDLEWARE = [
        ...
        ...
        ...

        "utilities.requestMW.GlobalRequest",
        'simple_history.middleware.HistoryRequestMiddleware',
        ...
        ...  
    ]
 ```
   
6. Add following variables to settings.py

```bash
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
}


AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = '*******-web-static'

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}


AWS_STATIC_LOCATION = 'static'
STATICFILES_STORAGE = 'utilities.storage_backends.StaticStorage'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)

AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'utilities.storage_backends.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'utilities.storage_backends.PrivateMediaStorage'

```

7. Delete all variables from db_config.py
8. Add following code to main urls.py (do the necessary imports)
```
Add URL-pattern to the urlpatterns of your Django project urls.py file 
* url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
* url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS

# any one time code should be run below
ProjectConfigurations.one_time_setup()
```
9. python manage.py migrate
10. If AWS setup is not available follow these steps
```
add these to local_settings.py 
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
```
11. python manage.py collectstatic