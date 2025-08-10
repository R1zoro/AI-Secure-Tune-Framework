# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container first
# This is a best practice for Docker layer caching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY app.py .

# Define an environment variable for the model path inside the container.
# This makes our container more flexible.
ENV MODEL_PATH=/app/models/distilgpt2

# Make port 5000 available to the host machine
EXPOSE 5000

# The command to run when the container starts.
# We use gunicorn for a more robust web server than Flask's default.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]