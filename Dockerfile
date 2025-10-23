# Use Python 3.11 or newer
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Start the Daphne ASGI server (supports WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "myproject1.asgi:application"]
