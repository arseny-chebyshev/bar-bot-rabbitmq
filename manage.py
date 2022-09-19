def init_django():
    import django
    import os
    from dotenv import load_dotenv
    from django.conf import settings
    load_dotenv()

    if settings.configured:
        return

    settings.configure(
        INSTALLED_APPS=[
            'db',
        ],
        DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        #'HOST': os.getenv('DB_HOST', 'localhost'), 
        # Docker запускает контейнер PostgreSQL не на 'localhost', 
        # а на имени контейнера в docker-compose: в данном случае, 'db'. 
        # https://stackoverflow.com/questions/70633841/django-docker-connection-to-server-at-localhost-127-0-0-1-port-5432-fail
        'HOST': 'bar-db',
        'PORT': os.getenv('DB_PORT'),
    }
}
    )
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    django.setup()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    init_django()
    execute_from_command_line()