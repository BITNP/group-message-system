# 自动将最新进度更新到compose所在文件夹目录下
set -e
cp database_design/createtable.sql compose/db/createdatabase.sql
cp database_design/privileges.sql compose/db/privileges.sql

cp -r BackEnd/databaseIO compose/server/
cp BackEnd/requirements.txt BackEnd/server.py compose/server
cp BackEnd/config.json compose
