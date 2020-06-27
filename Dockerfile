FROM python:3.8-slim
RUN mkdir -p /project
WORKDIR /project

COPY aio_server.py .
COPY requirements.txt .
COPY KEYS.data .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "aio_server.py"]
