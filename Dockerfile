# Use the official Python base image as the foundation
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y libssl-dev libffi-dev python3-dev

# Copy the requirements.txt file and install Python dependencies
COPY ./fast_dolphin_personal_training/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code and files
COPY ./fast_dolphin_personal_training /app/

# Set environment variables
ENV TELEGRAM_TOKEN=$TELEGRAM_TOKEN
ENV ADMIN_CHAT_ID=$ADMIN_CHAT_ID
ENV ADMIN_NAME=$ADMIN_NAME
ENV BACKEND_API=$BACKEND_API
ENV PERSONAL_TRAINING_ENDPOINT=$PERSONAL_TRAINING_ENDPOINT
ENV PERSONAL_TRAINING_REPORT=$PERSONAL_TRAINING_REPORT
ENV CURRENT_PERSONAL_TRAINING_ENDPOINT=$CURRENT_PERSONAL_TRAINING_ENDPOINT
ENV OPENAI_API_KEY=$OPENAI_API_KEY

# Run the Telegram bot
CMD ["python", "main.py"]