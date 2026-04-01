FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr for immediate logging
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces expects the web server to run on port 7860
EXPOSE 7860
CMD ["python", "app.py"]
