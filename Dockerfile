FROM python:3.6.5

COPY . /
RUN pip install -r /requirements.txt
EXPOSE 5000

# Build : docker build --tag auth_service .
# Run   : docker run --detach -p 5000:5000 auth_service

CMD ["gunicorn", "-b", "--worker-class", "gevent", "--log-level", "debug", "0.0.0.0:5000", "app.app:app"]