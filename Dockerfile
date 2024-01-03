# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Generate SSL/TLS certificates (for testing purposes)
RUN openssl req -x509 -newkey rsa:4096 -nodes -out /app/cert.pem -keyout /app/key.pem -days 365

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run Uvicorn with SSL
CMD ["uvicorn", "aat_backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/key.pem", "--ssl-certfile", "/app/cert.pem", "--workers", "4", "--reload"]
