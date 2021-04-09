FROM python:3.7-alpine

WORKDIR /app
COPY src/handler.py .

RUN apk add gcc musl-dev

ADD requirements.txt /
RUN pip install -r /requirements.txt

RUN apk del gcc musl-dev
ENTRYPOINT [ "kopf", "run", "/app/handler.py", "--verbose", "--all-namespaces"]
