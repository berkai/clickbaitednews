FROM python:3.6-buster

COPY bots/config.py /bots/
COPY bots/hash_table.txt /bots/
COPY bots/arial.ttf /bots/
COPY bots/stream_mentions.py /bots/
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /bots
CMD ["python3", "stream_mentions.py"]

