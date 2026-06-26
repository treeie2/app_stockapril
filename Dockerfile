FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
RUN mkdir -p data_cache
EXPOSE 8080
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8080", "-w", "2", "--timeout", "120"]
