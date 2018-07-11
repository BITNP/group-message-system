# 这句语句告诉bash如果任何语句的执行结果不是true则应该退出
set -e
mysql -uroot -p${MYSQL_ROOT_PASSWORD} <<EOF
source ${SCRIPT_PATH}/createdatabase.sql
source ${SCRIPT_PATH}/privileges.sql
EOF
