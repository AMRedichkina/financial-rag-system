# Use official Python image
FROM python:3.10-slim

# Set workdir to app root
WORKDIR /app

# Copy everything into /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure app is in PYTHONPATH
ENV PYTHONPATH=/app

# Expose FastAPI default port
EXPOSE 80

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
