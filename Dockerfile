FROM python:3.13-alpine

LABEL authors="Jinx@qqAys"

WORKDIR /usr/src/transmail-station

COPY . .

RUN apk update && \
    apk add --no-cache curl && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/cache/apk/* /tmp/* /root/.cache/pip

ENV TRANSMAIL_STATION_VERSION=0.0.7

EXPOSE 8100

CMD ["python", "-m", "app.main"]
