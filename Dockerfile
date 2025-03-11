FROM python:3.13-alpine

LABEL authors="Jinx@qqAys"

ENV TZ Asia/Shanghai

WORKDIR /usr/src/transmail-station

COPY . .

RUN sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache curl && \
    pip install -i https://mirrors.aliyun.com/pypi/simple --no-cache-dir -r requirements.txt && \
    rm -rf /var/cache/apk/* /tmp/* /root/.cache/pip

EXPOSE 8100

CMD ["python", "-m", "app.main"]
