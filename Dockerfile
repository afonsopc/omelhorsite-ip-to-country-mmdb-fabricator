FROM python:alpine

WORKDIR /app

ADD requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ADD create_mmdb.py /app/

CMD ["python3", "create_mmdb.py"]