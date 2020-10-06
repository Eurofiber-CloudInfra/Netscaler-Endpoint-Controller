FROM python:3.7
ADD . /src
RUN pip install kopf requests
CMD kopf run /src/handlers.py --verbose