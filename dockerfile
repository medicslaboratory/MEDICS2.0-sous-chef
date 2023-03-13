FROM python:3.9-slim

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /requirements.txt

COPY app /app

ENTRYPOINT [ "python3" ]
