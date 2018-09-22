# 2018-06-30 16:48:37 做sql最佳实践

import MySQLdb

conn = MySQLdb.connect(host='127.0.0.1', user="user", passwd='password',
                               db='groupMessage', charset='utf8', port=32768)

conn.autocommit(True)

cur = conn.cursor()

cur.execute('select * from User where id = 1')
print(cur.fetchone())
cur.close()

def update_tpl_from_database(newList,id):

    cur = conn.cursor()
    update_statement = 'UPDATE User set tplIDList= %s WHERE id = %s'
    res = cur.execute(update_statement,(newList,id))
    conn.commit()
    print(res)

    cur.close()
    return 

# 测试回滚功能

def test():
    pass