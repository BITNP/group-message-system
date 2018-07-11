FROM python:3.5-alpine
COPY requirements.txt /
COPY databaseIO /databaseIO/
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add mariadb-dev gcc musl-dev && \
    pip install -r /requirements.txt
COPY server.py config.json /
EXPOSE 29999
CMD ["python","/server.py"]