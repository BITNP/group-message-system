"封装对数据库的操作"

import MySQLdb


class databaseIO:

    def __init__(self, hostname, user, passwd, db=None, port=3306, charset='utf8'):
        """
        将数据库连接信息保存，并且会尝试连接一次数据库，有异常会抛出错误
            :param self: 
            :param hostname: host 
            :param user: 
            :param passwd: 
            :param db=None: 
            :param port=3306: 
            :param charset='utf8': 
        """
        self.host, self.user, self.passwd, self.db, self.port, self.charset = hostname, user, passwd, db, port, charset
        self.conn = MySQLdb.connect(
            host=hostname, user=user, passwd=passwd,
            db=db, port=port, charset=charset)
        self.conn.close()

    def _connect(self):
        """
        连接数据库
            :param self: 
        """
        self.conn = MySQLdb.connect(host=self.host, user=self.user,
                                    passwd=self.passwd, db=self.db, port=self.port, charset=self.charset)

    def _close(self):
        """
        断开数据库连接在最后调用
            :param self: 
        """
        self.conn.close()

    def identifyUser(self, username, password):
        """
        判断是否为用户
            :param self: 
            :param username: 
            :param password:
            :ret: 如果非法用户则为None 合法用户则返回id 
        """
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
            return res[0]

    def isSingle(self, extend: int):
        """
        查询该extend是否是单词发送，被回复调用
            :param self: 
            :param extend:int: 默认存在
        """
        self._connect()

        cur = self.conn.cursor()
        cur.execute('select count from SendStat where extend = %s', (extend,))
        count = cur.fetchone()[0]
        cur.close()

        self._close()
        if count == 1:
            return True
        else:
            return False

    def addReply(self, extend: int, reply: str, mobile: str = None):
        """
        根据参数自动添加回复，如果是单人不需要mobile
            :param self: 
            :param extend:int: 
            :param reply:str: 
            :param mobile:str=None: 
        """
        isSingle = self.isSingle(extend)

        self._connect()
        cur = self.conn.cursor()
        if isSingle:
            res = cur.execute('UPDATE SendStat SET reply = %s where extend = %s ',
                              (reply, extend)
                              )
        else:
            res = cur.execute('UPDATE GroupData SET reply = %s where extend = %s and mobile = %s', (reply, extend, mobile)
                              )
        self.conn.commit()
        cur.close()

        self._close()
        return res

    def getUserTpl(self, id: int):
        """
        得到以列表形式存储的模板编号
            :param self: 
            :param id:int: 
        """
        self._connect()
        cur = self.conn.cursor()
        cur.execute(
            'select group_concat(tpl_id) from Tpl where (id = %s and public = 0) or public = 1',
            (id,)
        )
        res = cur.fetchone()
        res = ('',) if res[0] is None else res
        cur.close()
        self._close()

        return list(set(res[0].split(',')))

    def getUserInfo(self, id: int):
        """
        获得User表用户信息，默认id正确
            :param self:
            :param id:int:
            :ret: fee,paid,createTime,remark
        """
        self._connect()

        cur = self.conn.cursor()
        cur.execute(
            'select fee,paid,createTime,remark from User \
             where id = %s limit 1',
            (id,))
        res = cur.fetchone()
        cur.close()
        self._close()
        return res

    def addUserTpl(self, id: int, tpl_id: int,  text, result, errmsg,
                   status, ifpublic=0, title='', remark=''):
        """
        添加模板，在完成api调用后使用，默认id存在
            :param self: 
            :param id:int: 
            :param tpl_id:int: 
            :param text: 
            :param result: 
            :param errmsg: 
            :param status: 
            :param ifpublic=0: 
            :param title='': 
            :param remark='':
            :ret: affect row number
        """
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'INSERT INTO Tpl(id,tpl_id,text,result,errmsg,status,public,title,remark) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (id, tpl_id, text, result, errmsg, status, ifpublic, title, remark)
        )
        self.conn.commit()
        cur.close()
        self._close()
        return res

    def deleteUserTpl(self, id: int, tpl_id: int):
        """
        删除tpl_id为tpl_id的行，要同时匹配id
            :param self:
            :param tpl_id:int:
        """
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'DELETE FROM Tpl where id = %s and tpl_id = %s ',
            (id, tpl_id)
        )
        self.conn.commit()
        cur.close()
        self._close()
        return res

    def addUserPaid(self, id: int, add_paid: float):
        """
        增加已付金额，默认id正确
            :param self:
            :param id:int:
            :param add_paid:float:
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

    def getUserHighestExtend(self):
        """
        获得最大的Extend值
            :param self: 
        """
        self._connect()

        cur = self.conn.cursor()
        cur.execute(
            'select extend from SendStat order by extend DESC limit 1')
        res = cur.fetchone()
        res = 0 if res is None else res[0]
        cur.close()

        self._close()
        return int(res)

    def checkUserBalance(self, id):
        """
        返回应缴费金额
            :param self: 
            :param id: 
        """
        fee, paid, *_ = self.getUserInfo(id)
        return fee-paid

    def SendSingle(self, id: int, mobile: str, ext, param: list, tpl_id: None, content: str, fee: float, totalCount: int, sid: str, result: int, errmsg: str):
        """
        发送单条信息后调用,注意：这里插入的extend值就是getHighestextend()的值+1
            :param self: 
            :param id:int: 
            :param mobile:str: 
            :param ext: 可空
            :param param:list: list形式，将转为字符串 
            :param tpl_id:None: 与后者二选一
            :param content:str: 
            :param fee:float: 
            :param totalCount:int: 
            :param sid:str: 必填
            :param result:int: 填写
            :param errmsg:str:
        """
        extend = self.getUserHighestExtend() + 1
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'Insert into SendStat(extend,id,ext,param,tpl_id,content,fee,count,totalCount,mobile,sid,result,errmsg) ' +
            'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (extend, id, ext, str(param), tpl_id, content, fee, 1, totalCount, mobile, sid, result, errmsg))
        cur.execute(
            'UPDATE User SET fee=User.fee+%s WHERE id = %s',
            (fee, id)
        )
        self.conn.commit()
        cur.close()

        self._close()
        return res  # 返回 uid

    def SendMulti(self, id: int, ext: str, tpl_id: int, content: str, fee: float, totalCount: int, data_list: list):
        """
        发送多个后调用
            :param self: 
            :param id:int: 
            :param ext:str: 
            :param tpl_id:int:
            :param content:str: 
            :param fee:float: 
            :param totalCount:int: 
            :param data_list:list: 字典列表，包括 sid,param,mobile,result,fee,errmsg
            :ret: 插入行数
        """
        extend = self.getUserHighestExtend()+1
        self._connect()

        cur = self.conn.cursor()

        cur.execute(
            'Insert into SendStat(extend,id,ext,tpl_id,content,fee,count,totalCount)\
             values(%s,%s,%s,%s,%s,%s,%s,%s)',
            (extend, id, ext, tpl_id, content, fee, len(data_list), totalCount)
        )
        multi_info = [(id, extend, i['mobile'], i['sid'], i['result'], i['fee'], i['errmsg'], i['param']) for i in data_list
                      ]
        # print('\n',multi_info)
        res = cur.executemany(
            'INSERT into GroupData(id,extend,mobile,sid,result,fee,errmsg,param) values(%s,%s,%s,%s,%s,%s,%s,%s)',
            multi_info
        )
        self.conn.commit()
        cur.close()

        self._close()
        return res

    def InsertUser(self, username: str, password: str, remark: str):
        """
        插入用户，管理员使用
            :param self: 
            :param username:str: 
            :param password:str: 
            :param remark:str: 
        """
        self._connect()

        cur = self.conn.cursor()
        res = cur.execute(
            'insert into User(username,password,remark) values(%s,%s,%s)', (username, password, remark))
        self.conn.commit()
        cur.close()

        self._close()
        return res


if __name__ == '__main__':
    run = databaseIO('172.18.0.1', 'root', 'password',
                     db='groupMessage', port=32778)

    run.InsertUser('wangxie', 'md5', 'aaa')
    run.InsertUser('shetuan1', 'md6', 'bbb')
    run.InsertUser('shetuan2', 'md7', 'ccc')

    data = [
        dict(code=1, sid=123, mobile='112', fee=0.05, msg='1sda'),
        dict(code=1, sid=1234, mobile='224', fee=0.05, msg='1sdsda'),
        dict(code=1, sid=1253, mobile='444', fee=0.05, msg='1ssda')
    ]
    # run.addUserTpl(2,22433234,'hhhh',0,'success',0,ifpublic=0)
    # run.deleteUserTpl(2,2324)
    # run.addUserPaid(1, 0.04)
    # run.SendSingle(1, '123', '', None, 22433234, '',
    #                0.04, 3, 3, 'aasdf', 1, 'suc')
    # print(run.getUserHighestExtend())
    # print(run.checkUserBalance(1))
    # print(run.isSingle(2))
    # uid = (run.beforeSendSingle(1, '1123', 'hh'))
    # print(run.afterSendSingle(1,uid,0.02,1,2,'saf'))
