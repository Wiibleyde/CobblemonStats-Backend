# Use a Python 3.8 runtime as a base image
FROM python:3.11.2
WORKDIR /app

# Copy the requirements file and install the necessary packages
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Copy the source code, configuration file, and database file
COPY . .

EXPOSE 5000

# Set environment variables
ENV BASE_SERVER_PATH=./
ENV HOST=0.0.0.0
ENV PORT=5000
ENV DEBUG=False

# Start the bot
CMD ["python", "main.py"]