# 1. Use the official Python image. 
# We use 'slim' to keep the file size small for faster deployments.
FROM python:3.13-slim

# 2. Set the directory inside the container where your code will live.
WORKDIR /app

# 3. Copy your local files (main.py, requirements.txt) into the container.
COPY . .

# 4. Install the libraries listed in your requirements.txt file.
RUN pip install --no-cache-dir -r requirements.txt

# 5. This command tells Cloud Run to start your 'Brain' using Gunicorn.
# Gunicorn is a professional-grade server that is more stable than the basic Flask runner.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app