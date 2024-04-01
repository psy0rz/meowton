FROM docker.io/zauberzeug/nicegui:latest

USER root
RUN apt update && apt install build-essential -y

ENTRYPOINT /usr/local/bin/python -u main.py

COPY ../requirements.txt /app
RUN pip install -r /app/requirements.txt

