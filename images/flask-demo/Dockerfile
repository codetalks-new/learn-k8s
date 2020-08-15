FROM python:3.8.5-alpine3.12
ENV PYTHONUNBUFFERED 1

RUN pip install flask==1.1.2
ENV FLASK_APP=app.py
RUN mkdir /app
ADD app.py /app
WORKDIR /app
CMD flask run --host=0.0.0.0 --port=5000

