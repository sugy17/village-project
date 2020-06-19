FROM python:3.6

COPY . ./

RUN pip install -r requirements.txt

CMD ["python", "test_api.py"]