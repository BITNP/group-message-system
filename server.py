from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import requests
import MySQLdb
import hashlib

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


def process_resquest(dict_data):
    code = str(dict_data['request_code'])
    if code == '4':
        response = requests.post(
            'https://sms.yunpian.com/v2/sms/get_record.json', data=dict_data)
    elif code == '2.1':
        response = requests.post(
            'https://sms.yunpian.com/v2/tpl/get_default.json', data=dict_data)
    elif code == '2.2':
        response = requests.post(
            'https://sms.yunpian.com/v2/tpl/get.json', data=dict_data)
    elif code == '7':
        response = requests.post(
            'https://sms.yunpian.com/v2/sms/get_total_fee.json', data=dict_data)
    else:
        return None
    return response


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

    def do_GET(self):
        print(str(self.path), str(self.headers))
        self._set_headers()
        self.wfile.write("GET request for {}".format(
            self.path).encode('utf-8'))

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
                print('testpoint', dict_data)
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

        # 判断是否存在request_code
        if 'request_code' not in dict_data:
            self._set_headers(False)
            self.wfile.write(
                '{"code":253,"msg":"没有request_code"}'.encode('utf-8'))
            return

        # step 1 : 从数据库验证身份，提取信息
        if 'username' not in dict_data or 'password' not in dict_data:
            self._set_headers(False)
            self.wfile.write(
                '{"code":251,"msg":"no username or password"}'.encode('utf-8'))
            return

        # 防注入 TODO
        query_statement = 'SELECT username,password,extend,uid,tplIDList from User where username = '+'"'+str(dict_data['username'])+'"' + \
            'and password  = '+'"'+str(dict_data['password'])+'" limit 1'
        print(query_statement)
        conn.query(query_statement)

        result = conn.use_result()
        res = result.fetch_row()
        if len(res) > 0:
            *_, user_extend, user_uid, user_tplIDList = res[0]
            print(user_extend, user_tplIDList)
            print('验证成功')

        else:
            self._set_headers(False)
            self.wfile.write(
                '{"code":252,"msg":"error username or password"}'.encode('utf-8'))
            return
        # print(hashlib.md5("whatever your string is".encode('utf-8')).hexdigest())

        # step 2 : 处理后续信息，发送api

        # step 3 : 如果有需要，过滤响应结果并返回；如果没有需要，直接返回

        dict_data.update(dict(apikey=apikey))
        print(dict_data)
        response = process_resquest(dict_data)
        if response == None:
            self._set_headers(False)
            self.wfile.write(
                '{"code":254,"msg":"error request_code"}'.encode('utf-8'))
            return
        print(response.text)
        self._set_headers()
        self.wfile.write(response.text.encode('utf-8'))  # 向前端回传数据的格式


def run(server_class=HTTPServer, handler_class=MyRequestHandler):
    httpd = server_class(ADDR, handler_class)

    print('waiting for connecting...')
    httpd.serve_forever()
    httpd.server_close()


def init():
    """
    初始化数据库
    """
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user="user", passwd='password',
                               db='groupMessage', charset='utf8', port=32768)
    except MySQLdb.OperationalError as e:
        print('数据库连接失败', e)
        exit(1)
        return None
    else:
        return conn


if __name__ == '__main__':
    from sys import argv
    conn = init()
    if len(argv) == 2:
        run()
    else:
        run()
