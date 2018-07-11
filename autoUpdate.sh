# 自动将最新进度更新到compose所在文件夹目录下

mkdir -p compose/db/
cp database_design/createtable.sql compose/db/createdatabase.sql
cp database_design/privileges.sql compose/db/privileges.sql

mkdir -p compose/server/databaseIO
cp -r BackEnd/databaseIO compose/server/databaseIO
cp BackEnd/config.json BackEnd/requirements.txt BackEnd/server.py compose/server

