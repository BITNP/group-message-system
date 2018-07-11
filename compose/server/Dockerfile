FROM python:3.5-alpine

MAINTAINER FengKaiyu <loveress01@gmail.com>

COPY requirements.txt /
COPY databaseIO /databaseIO/
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add mariadb-dev gcc musl-dev && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /requirements.txt
COPY server.py /
CMD ["python","/server.py"]