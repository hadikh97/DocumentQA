#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL is available"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

exec "$@"
