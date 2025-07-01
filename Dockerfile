FROM python:3.10-slim

WORKDIR /app

# ✅ Install PostgreSQL dev libs and compiler (required for psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

# 📦 Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copy Django app
COPY . .

# (Optional) Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
