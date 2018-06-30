"封装对数据库的操作"

import MySQLdb
import json


class databaseIO:
    def __init__(self, hostname, user, passwd, db=None, port=3306, charset='utf8'):
        self.host, self.user, self.passwd, self.db, self.port, self.charset = hostname, user, passwd, db, port, charset
        self.conn = MySQLdb.connect(
            host=hostname, user=user, passwd=passwd, db=db, port=port, charset=charset)
        self.conn.close()

    def _connect(self):
        self.conn = MySQLdb.connect(host=self.host, user=self.user,
                                    passwd=self.passwd, db=self.db, port=self.port, charset=self.charset)

    def _close(self):
        self.conn.close()

    def identfyUser(self, username, password):
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'select id from User where username = %s and password = %s limit 1', (username, password))
        if res == 0:
            cur.close()
            self._close()
            return None
        else:
            res = cur.fetchone()
            cur.close()
            self._close()
            return res

    def getUserInfo(self, id: int):
        """
        获得User表用户信息，默认id正确
            :param self: 
            :param id:int: 
        """
        self._connect()

        cur = self.conn.cursor()
        cur.execute(
            'select fee,tplIDList,createTime,remark from User where id = %s limit 1', (id,))
        res = cur.fetchone()
        cur.close()

        self._close()
        return res

    def getUserHighestUid(self, id):
        self._connect()

        cur = self.conn.cursor()
        cur.execute(
            'select uid from SendStat where id = %s order by uid DESC limit 1', (id,))
        res = cur.fetchone()
        res = 0 if res is None else res[0]
        cur.close()

        self._close()
        return res

    def beforeSendSingle(self, id: int, mobile: str, text: str):

        next_uid = self.getUserHighestUid(id)+1  # 函数内对conn的操作有影响 TODO

        self._connect()

        cur = self.conn.cursor()

        res = cur.execute(
            'Insert into SendStat(id,uid,mobile,content) values(%s,%s,%s,%s)', (id, next_uid, mobile, text))
        self.conn.commit()
        cur.close()

        self._close()
        return next_uid  # 返回 uid

    def afterSendSingle(self, id, uid, fee, sid, code, msg):
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'update SendStat set fee=SendStat.fee+%s,sid=%s,code=%s,msg=%s where id = %s and uid = %s', (
                fee,sid,code,msg,id, uid)
        )
        res = cur.execute('update User set fee=User.fee+%s where id = %s',(fee,id))
        self.conn.commit()
        cur.close()

        self._close()
        return res  # 返回 uid

    def InsertUser(self, username: str, password: str, remark: str):
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'insert into User(username,password,remark) values(%s,%s,%s)', (username, password, remark))
        self.conn.commit()
        cur.close()

        self._close()
        return res


if __name__ == '__main__':
    run = databaseIO('172.17.0.1', 'user', 'password',
                     db='groupMessage', port=32768)

    # run.InsertUser('wangxie','md5','aaa')
    # run.InsertUser('shetuan1','md6','bbb')
    # run.InsertUser('shetuan2','md7','ccc')

    uid = (run.beforeSendSingle(1, '1123', 'hh'))
    print(run.afterSendSingle(1,uid,0.02,1,2,'saf'))
