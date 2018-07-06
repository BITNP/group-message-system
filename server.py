from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import requests
import MySQLdb
import hashlib
import databaseIO.databaseIO as dbIO

HOST = ''
PORT = 29999
ADDR = (HOST, PORT)

# HTTP/1.1 404 Not Found
# Server: 360wzws
# Date: Fri, 29 Jun 2018 15:33:21 GMT
# Content-Type: text/html
# Content-Length: 479
# Connection: close
# X-Powered-By-360WZB: wangzhan.360.cn
# ETag: "5a7e7448-1df"
# WZWS-RAY: 114-1530315201.377-s9lfyc2

with open('config.json') as f:
    apikey = json.load(f)['apikey']
start_time = '2018-06-11 00:00:00'
end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def replaceText(raw_text, replaceTo: list, whereToReplace: list):
    text = raw_text
    for i in range(len(whereToReplace)):
        text = text.replace(whereToReplace[i], replaceTo[i])
    return text


def process_resquest(dict_data):
    code = str(dict_data['request_code'])
    if code == '1.5':
        response = requests.post(
            'https://sms.yunpian.com/v2/sms/get_record.json', data=dict_data)
    elif code == '1.4':
        """
        注意，mobile要以逗号分割字符串形式传入（仅云片网，
        param要以列表的形式传入（云片网,也就是tpl_value
        """
        payload = dict(apikey=dict_data['apikey'],
                       mobile=','.join(dict_data['mobile'])
                       )
        text_list = [replaceText(
            dict_data['content'], param, dict_data['replace']) for param in dict_data['param']]
        payload['text'] = ','.join(text_list)
        print(payload)
        response = requests.post(
            'https://sms.yunpian.com/v2/sms/multi_send.json', data=payload
        )
        dict_result = response.json()
        print(response.json())
        if 'http_status_code' in dict_result:  # api调用正确，但有其他错误
            return json.dumps(dict_result, ensure_ascii=False)

        result_data = [dict(sid=i['sid'], param=str(j), mobile=i['mobile'], result=i['code'], errmsg=i['msg'], fee=i['fee'])
                       for i, j in zip(dict_result['data'], dict_data['param'])
                       ]

        db.Send(dict_data['id'], '', 1, None, dict_data['content'], dict_result['total_fee'],
                dict_result['total_count'], result_data)
    elif code == '1.1':
        response = requests.post(
            'https://sms.yunpian.com/v2/tpl/get_default.json', data=dict_data)
    elif code == '1.2':
        response = requests.post(
            'https://sms.yunpian.com/v2/tpl/get.json', data=dict_data)
        print(response.json())
        # 按照tplIDList 处理 TODO
        tpl_list = db.getUserTpl(dict_data['id'], 1)
        print('数据库中存储的', tpl_list)
        result = response.json()
        # 异常处理
        if 'http_status_code' in result:
            return json.dumps(result, ensure_ascii=False)

        if isinstance(result, dict):
            result = [result]
        # 下面一条语句起到过滤作用，注意生产环境中要取消注释
        # result = list(filter(lambda x: str(x['tpl_id']) in tpl_list, result))

        return json.dumps(result, ensure_ascii=False)

    elif code == '1.3':
        response = requests.post(
            'https://sms.yunpian.com/v2/tpl/add.json', data=dict_data)
        dict_result = response.json()
        print(dict_result)
        if 'http_status_code' in dict_result:  # api调用正确，但有其他错误
            return '{"code":234,"msg":"'+dict_result['detail']+'"}'


        affect_row_num = db.addUserTpl(
            dict_data['id'], dict_result['tpl_id'], 1, dict_result['tpl_content'],
            None, dict_result['check_status'], None)
        print(affect_row_num)
        return '{"success":true}'
    elif code == '6':
        res = db.checkSendResult(dict_data['id'])
        return json.dumps(res)
    elif code == '7':
        fee, paid, *_ = db.getUserInfo(dict_data['id'])
        return json.dumps(dict(fee=float(fee), paid=float(paid)))
    else:
        return None
    return response.text


class MyRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):

        super(MyRequestHandler, self).__init__(request, client_address, server)

    def _set_headers(self, status=True):
        if not status:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            return
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

    def _check_dict(self, data: dict, *args):
        for i_str in args:
            if i_str not in data:
                self._set_headers(False)
                string = '{"code":251,"msg":"'+i_str+' not in json"}'
                self.wfile.write(string.encode())
                return False
        return True

    def do_GET(self):
        print(str(self.path), str(self.headers))
        self._set_headers()
        # self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        # 后续可能要使用配置文件
        json_string = '{"api":["云片网(不支持回复)","腾讯（支持回复）"],"new_qt_version":"0.5.0"}'
        self.wfile.write(json_string.encode())
    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):

        def process_json(raw_data):
            try:
                dict_data = json.loads(raw_data)
            except:
                self._set_headers(False)
                # 异常处理 TODO
                return None, False
            else:
                dict_data.update(
                    dict(apikey=apikey, start_time=start_time, end_time=end_time))
            return dict_data, True

        # Doesn't do anything with posted data

        # step 0 : 处理json数据，转化成字典，异常则直接退出
        # <--- Gets the size of data
        content_length = int(self.headers['Content-Length'])
        # <--- Gets the data itself
        post_data = self.rfile.read(content_length)
        dict_data, status = process_json(post_data)

        if not status:
            self.wfile.write('{"code":250,"msg":"非json格式"}'.encode('utf-8'))
            return

        # step 1 : 从数据库验证身份，提取信息
        if not self._check_dict(dict_data, "username", "password", "request_code"):
            return

        myid = db.identifyUser(dict_data['username'], dict_data['password'])

        if myid is not None:
            myinfo = db.getUserInfo(myid)
            print('get info :', myinfo)
            print('验证成功')
        else:
            self._set_headers(False)
            self.wfile.write(
                '{"code":252,"msg":"error username or password"}'.encode('utf-8'))
            return
        # print(hashlib.md5("whatever your string is".encode('utf-8')).hexdigest())

        # step 2 : 处理后续信息，发送api
        dict_data.update(dict(apikey=apikey, id=myid))
        print(dict_data)
        # step 3 : 如果有需要，过滤响应结果并返回；如果没有需要，直接返回

        response_text = process_resquest(
            dict_data)

        if response_text is None:
            self._set_headers(False)
            self.wfile.write(
                '{"code":254,"msg":"error request_code"}'.encode())
            return
        print(response_text)
        self._set_headers()
        self.wfile.write(response_text.encode())  # 向前端回传数据的格式


def run(server_class=HTTPServer, handler_class=MyRequestHandler):
    """
    运行监听
        :param server_class=HTTPServer: 
        :param handler_class=MyRequestHandler: 
    """
    httpd = server_class(ADDR, handler_class)
    print('waiting for connecting...')
    httpd.serve_forever()
    httpd.server_close()


def init():
    """
    初始化数据库
    """
    try:
        db = dbIO.databaseIO('172.18.0.1', 'root',
                             'password', 'groupMessage', 32771)
    except MySQLdb.OperationalError as e:
        print('数据库连接失败', e)
        exit(1)
        return None
    else:
        return db


if __name__ == '__main__':
    from sys import argv
    db = init()
    run()
