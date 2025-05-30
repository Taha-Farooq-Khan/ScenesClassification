# Use a lightweight Python 3.9 image
FROM python:3.9-slim

# Update the package list and install essential system packages
RUN apt-get install -y \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
ENV PIP_DEFAULT_TIMEOUT=1000
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# List the contents of the working directory (for debugging)
RUN ls -la $APP_HOME/

# Run the Flask app on container startup
CMD [ "python", "app.py" ]
