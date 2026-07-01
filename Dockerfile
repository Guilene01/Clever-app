# Stage 1: compile TypeScript → static/js/
FROM node:20-slim AS frontend
WORKDIR /app
COPY package.json ./
RUN npm install
COPY tsconfig.json ./
COPY apps/notes/static_src/ apps/notes/static_src/
RUN npm run build

# Stage 2: production image
FROM python:3.12-slim AS app
WORKDIR /app

# Non-root user for the container process
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Pull compiled JS from the frontend stage
COPY --from=frontend /app/static/ ./static/

# collectstatic needs a key at build time; the real key is injected at runtime
RUN DJANGO_SECRET_KEY=dummy-build-only \
    DJANGO_DEBUG=false \
    python manage.py collectstatic --noinput

USER appuser

EXPOSE 8000
CMD ["gunicorn", "notesy.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120"]
