FROM python:3.7-alpine
WORKDIR /app
COPY src/handler.py .
RUN apk add gcc musl-dev
RUN pip install kopf requests
RUN apk del gcc
ENTRYPOINT [ "kopf", "run", "/app/handler.py", "--verbose"]