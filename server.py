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


def tplIDList2list(tpl: str):
    return tpl.split(',')


def list2tplIDList(li: list):
    li = [str(i) for i in li]
    return ','.join(li)


def get_info_from_database(uname, pword):
    """
    Docstring here.

        :param uname: 
        :param pword:
        :ret 元组 或 None 
    """
    cur = conn.cursor()
    query_statement = 'SELECT username,password,id,extend,uid,tplIDList from User where username = %s and password = %s limit 1'
    cur.execute(query_statement, (uname, pword))
    return cur.fetchone()

def update_tpl_from_database(newList,id):

    cur = conn.cursor()
    print(newList,id)
    update_statement = 'UPDATE User set tplIDList= %s WHERE id = %s'
    affect_row_num = cur.execute(update_statement,(newList,id))
    conn.commit()
    cur.close()
    return affect_row_num

def process_resquest(dict_data, tplIDList, user_id):
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
        # 按照tplIDList 处理 TODO
        tpl = tplIDList2list(tplIDList)
        # 没有处理异常 TODO
        result = response.json()

        # if 'http_status_code' in result: # api调用正确，但有其他错误
        #     return json.dumps(result,ensure_ascii=False)
        result = list(filter(lambda x: x['tpl_id'] in tpl, result))
        return json.dumps(result, ensure_ascii=False)

    elif code == '2.3':
        response = requests.post(
            'https://sms.yunpian.com/v2/tpl/add.json', data=dict_data)
        tpl = tplIDList2list(tplIDList)
        # 没有异常处理 TODO
        dict_result = response.json()

        if 'http_status_code' in dict_result:  # api调用正确，但有其他错误
            return json.dumps(dict_result, ensure_ascii=False)
        
        print(dict_result)
        tpl.append(dict_result['tpl_id'])
        affect_row_num = update_tpl_from_database(list2tplIDList(tpl),user_id)
        print(affect_row_num)
        return json.dumps(dict_result, ensure_ascii=False)

    elif code == '7':
        response = requests.post(
            'https://sms.yunpian.com/v2/sms/get_total_fee.json', data=dict_data)
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

        res = get_info_from_database(str(dict_data['username']),str(dict_data['password']))

        if res is not None :
            *_, user_id, user_extend, user_uid, user_tplIDList = res
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

        dict_data.update(dict(apikey=apikey, user_id=user_id))
        print(dict_data)
        response_text = process_resquest(
            dict_data, user_tplIDList, user_id=user_id)
        if response_text is None:
            self._set_headers(False)
            self.wfile.write(
                '{"code":254,"msg":"error request_code"}'.encode('utf-8'))
            return
        print(response_text)
        self._set_headers()
        self.wfile.write(response_text.encode('utf-8'))  # 向前端回传数据的格式


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
