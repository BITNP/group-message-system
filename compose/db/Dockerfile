FROM mariadb

MAINTAINER FengKaiyu <loveress01@gmail.com>

# 将setup.sh中的调用放入$SCRIPT_PATH
ENV SCRIPT_PATH /mysql
COPY privileges.sql createdatabase.sql $SCRIPT_PATH/

# 将被执行脚本放入entrypoint目录
COPY setup.sh /docker-entrypoint-initdb.d/
RUN chmod a+x /docker-entrypoint-initdb.d/setup.sh

ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 3306
CMD ["mysqld"]