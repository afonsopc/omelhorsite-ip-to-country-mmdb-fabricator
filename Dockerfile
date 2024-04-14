FROM python:alpine

WORKDIR /app

ADD requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ADD create_mmdb.py /app/
ADD run.py /app/

CMD ["python3", "run.py"]