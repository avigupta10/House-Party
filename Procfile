release: python manage.py migrate
web: gunicorn --pythonpath house_party house_party.wsgi --log-file -
