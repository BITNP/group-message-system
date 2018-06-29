from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import requests
import MySQLdb

HOST = ''
PORT = 80
ADDR = (HOST,PORT)

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

class MyRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self,status = True):
        if not status:
            self.send_response(404)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def do_GET(self):
        print(str(self.path),str(self.headers))
        self._set_headers()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
    
    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        
        def process_json(raw_data):
            try:
                dict_data = json.loads(raw_data)
            except:
                self._set_headers(False)
                # 异常处理 TODO
                return None,False
            else:
                print('testpoint',dict_data)
            dict_data.update(dict(apikey=apikey,start_time=start_time,end_time=end_time))
            return dict_data,True
        
        # Doesn't do anything with posted data
        
        # step 0 : 处理json数据，转化成字典，异常则直接退出
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        dict_data, status = process_json(post_data)

        if not status:
            self.wfile.write('{"code":250,"msg":"非json格式"}'.encode('utf-8'))
            return
        
        # step 1 : 从数据库验证身份，提取信息
        if 'username' not in dict_data or 'password' not in dict_data:
            self._set_headers(False)
            self.wfile.write('{"code":251,"msg":"no username or password"}'.encode('utf-8'))
            return
        # step 2 : 处理后续信息，发送api

        # step 3 : 如果有需要，过滤响应结果并返回；如果没有需要，直接返回
        
        self._set_headers()
        response = requests.post('https://sms.yunpian.com/v2/sms/get_record.json',data = dict_data)
        print(response.text)
        self.wfile.write(response.text.encode('utf-8')) # 向前端回传数据的格式

def run(server_class = HTTPServer, handler_class = MyRequestHandler):
    httpd = server_class(ADDR,handler_class)
    print('waiting for connecting...')
    httpd.serve_forever()
    httpd.server_close()

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run()        
    else:
        run()