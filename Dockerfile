FROM python:3.12-slim

WORKDIR /comp7940-lab
COPY requirements.txt .
COPY config.ini .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
CMD ["python", "chatbot.py"]