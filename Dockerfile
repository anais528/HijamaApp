# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code
COPY . .

# Expose the port that Flask listens on
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
