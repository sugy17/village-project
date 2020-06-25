FROM python:3.8-slim
RUN mkdir /project
WORKDIR /project

COPY aio_server.py .
COPY requirements.txt .
COPY KEYS.data .
RUN apt-get update -y && apt-get install -y build-essential python3-dev
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get remove -y build-essential python3-dev && apt-get -y autoremove 

CMD ["python", "aio_server.py"]
