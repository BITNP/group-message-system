"封装对数据库的操作"

import MySQLdb
import json


def tplIDList2list(tpl: str):
    return tpl.split(',')


def list2tplIDList(li: list):
    li = [str(i) for i in li]
    return ','.join(li)


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
            'select fee,paid,tplIDList,createTime,remark from User where id = %s limit 1', (id,))
        res = cur.fetchone()
        cur.close()
        res = (res[0], res[1], tplIDList2list(res[2]), res[3], res[4])
        self._close()
        return res

    def addToUserTpl(self, id: int, add_item: int or str):
        """
        获得User表用户信息，默认id正确
            :param self:
            :param id:int:
        """
        self._connect()

        cur = self.conn.cursor()
        cur.execute(
            'select tplIDList from User where id = %s limit 1', (id,))
        res = cur.fetchone()[0]
        res = str(add_item) if res == '' else res+','+str(add_item)
        # 去重？ 可选 TODO
        cur.execute(
            'update User set tplIDList = %s where id = %s', (res, id)
        )
        self.conn.commit()
        cur.close()
        self._close()
        return res

    def deleteFromUserTpl(self, id: int, delete_item: int or str):
        """
        获得User表用户信息，默认id正确
            :param self:
            :param id:int:
        """
        self._connect()

        cur = self.conn.cursor()
        cur.execute(
            'select tplIDList from User where id = %s limit 1', (id,))
        res = cur.fetchone()[0]
        list_res = list(set(tplIDList2list(res)) - set([str(delete_item)]))
        print(list_res)
        cur.execute(
            'update User set tplIDList = %s where id = %s', (list2tplIDList(
                list_res), id)
        )
        self.conn.commit()
        cur.close()
        self._close()
        return res

    def addUserPaid(self, id: int, add_paid: float):
        """
        获得User表用户信息，默认id正确
            :param self:
            :param id:int:
        """
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'update User set paid = User.paid+%s where id = %s', (add_paid, id)
        )
        self.conn.commit()
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

    def checkUserBalance(self, id):
        """
        返回应缴费金额
            :param self: 
            :param id: 
        """
        fee, paid, *_ = self.getUserInfo(id)
        return fee-paid

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

    def afterSendSingle(self, id, uid, fee, sid, code, msg, count):
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'update SendStat set fee=%s,sid=%s,code=%s,msg=%s,totalCount=%s where id = %s and uid = %s', (
                fee, sid, code, msg, count, id, uid)
        )
        res = cur.execute(
            'update User set fee=User.fee+%s where id = %s', (fee, id))
        self.conn.commit()
        cur.close()

        self._close()
        return res  # 返回 uid

    def beforeSendMulti(self, id, mobile_list: list, text):
        next_uid = self.getUserHighestUid(id)+1  # 函数内对conn的操作有影响 TODO

        self._connect()

        cur = self.conn.cursor()

        res = cur.execute(
            'Insert into SendStat(id,uid,count,content) values(%s,%s,%s,%s)', (id, next_uid, len(mobile_list), text))

        multi_info = [(id, next_uid, i) for i in mobile_list]

        res = cur.executemany(
            'INSERT into GroupData(id,uid,mobile) values(%s,%s,%s)', multi_info
        )
        self.conn.commit()
        cur.close()

        self._close()
        return next_uid  # 返回 uid

    def afterSendMulti(self, id, uid, total_count, total_fee, data: list):
        self._connect()

        cur = self.conn.cursor()

        res = cur.execute(
            'update SendStat set fee=%s,totalCount= %s where id = %s and uid = %s', (
                total_fee, total_count, id, uid)
        )

        multi_info = [
            (i['code'],i['msg'],i['fee'],i['sid'],id,uid,i['mobile']) for i in data
        ]
        cur.executemany(
            'update GroupData set code = %s,msg = %s, fee = %s,sid =%s where id = %s and uid = %s and mobile = %s',
            multi_info        
        )
        res = cur.execute(
            'update User set fee=User.fee+%s where id = %s', (total_fee, id))
        self.conn.commit()

        cur.close()

        self._close()
        return   

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

    run.InsertUser('wangxie','md5','aaa')
    run.InsertUser('shetuan1','md6','bbb')
    run.InsertUser('shetuan2','md7','ccc')
    run.addToUserTpl(1, 155)
    run.addUserPaid(1,0.04)

    data = [
        dict(code=1,sid = 123,mobile='112',fee=0.05,msg = '1sda'),
        dict(code=1,sid = 1234,mobile='224',fee=0.05,msg = '1sdsda'),
        dict(code=1,sid = 1253,mobile='444',fee=0.05,msg = '1ssda')
    ]

    uid = run.beforeSendMulti(1, ['112', '224', '444'], 'hello')
    run.afterSendMulti(1,uid,3,0.15,data)
    print(run.getUserInfo(1))
    print(run.checkUserBalance(1))
    # uid = (run.beforeSendSingle(1, '1123', 'hh'))
    # print(run.afterSendSingle(1,uid,0.02,1,2,'saf'))
