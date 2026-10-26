#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

if [ -f "RESET_DATA_TRIGGER" ]; then
    echo "RESET_DATA_TRIGGER topildi. Sayt ma'lumotlari tozalanmoqda..."
    python manage.py reset_site_data
fi


