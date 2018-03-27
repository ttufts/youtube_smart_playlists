FROM python:3
MAINTAINER thomas.j.tufts@gmail.com

RUN git clone https://github.com/ttufts/youtube_smart_playlists

VOLUME ["/config_data"]

COPY entrypoint.sh /entrypoint.sh
RUN chmod 700 /entrypoint.sh
