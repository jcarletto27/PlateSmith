# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5544

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5544"]
