FROM python:3.6
EXPOSE 8000
WORKDIR /app
ENV LANG en_US.UTF-8

RUN apt update \
    && apt install -y libgdal20 netcat postgresql-client locales-all \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install uwsgi

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

COPY . .

RUN DJANGO_SECRET_KEY=dummy ./manage.py compile_pyc

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
