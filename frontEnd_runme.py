# 可以直接根据xml运行代码，便于快速迭代开发
import sys
from PyQt5 import QtWidgets
from frontEnd_qt import Ui_MainWindow
import xlrd
import re
import requests
import json
import csv

VERSION = "1.0.0"
config_info = {}
try:
    with open('config.json') as f:
        config_info = json.load(f)
except:
    print('未能读取config.json')
URL = config_info['server_url'] if 'server_url' in config_info else 'http://localhost:29999'
UNAME = config_info['username'] if 'username' in config_info else ''
PWORD = config_info['password'] if 'password' in config_info else ''

def ifHasUpdate(new_version):
    if list(map(lambda x: int(x), VERSION.split('.'))) < list(map(lambda x: int(x), new_version.split('.'))):
        return '[有更新]请联系管理员'
    else:
        return '[客户端已是最新]'


class my_win(Ui_MainWindow):
    def open_excel(self):
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(
            None, "open file dialog", None, "Excel files(*.xls *.xlsx);;CSV file(*.csv)")  # 待修改或拓展 TODO
        if file_name == '':
            return
        if file_type == 'CSV file(*.csv)':
            try:
                datafile = open(file_name, "r")
                reader = csv.reader(datafile)
            except:
                word = '打开CSV文件失败'
            else:
                word = '[已打开]: '+file_name
                reader = list(reader)
                self.length, self.sheetncols = len(reader), len(reader[0])
                self.tableWidget.setRowCount(self.length)
                self.tableWidget.setColumnCount(self.sheetncols)
                self.tableWidget.setHorizontalHeaderLabels(['手机号'])
                # 垂直表头TODO
                for i in range(self.length):
                    for j in range(self.sheetncols):
                        newItem = QtWidgets.QTableWidgetItem(reader[i][j])
                        self.tableWidget.setItem(i, j, newItem)
        else:
            try:
                datafile = xlrd.open_workbook(file_name)
            except:
                word = '打开xls/xlsx文件失败'
            else:
                print(datafile.nsheets, datafile.sheet_names)
                sheet = datafile.sheets()[0]
                print(sheet.name)
                self.length, self.sheetncols = sheet.nrows, sheet.ncols
                self.tableWidget.setRowCount(sheet.nrows)
                self.tableWidget.setColumnCount(sheet.ncols)
                self.tableWidget.setHorizontalHeaderLabels(['手机号'])
                # 垂直表头TODO
                for i in range(sheet.nrows):
                    for j in range(sheet.ncols):
                        newItem = QtWidgets.QTableWidgetItem(
                            sheet.cell(i, j).value)
                        self.tableWidget.setItem(i, j, newItem)
                word = '[已打开]: '+file_name
        self.statusLineWords[3] = word
        if self.updateTplStatus(2) & 2:
            self.tableWidget.setHorizontalHeaderLabels(
                ['手机号']+self.substite_list)
        self.updateStatueLine(0)

        print(file_name, file_type)

    def popup(self):
        # QtWidgets.QMessageBox.question(None,"Pyqt","information") # information, question, warnaing
        form = QtWidgets.QFormLayout(QtWidgets.QDialog())

        pass

    def change(self):
        pass
        # self.tableWidget.setRowCount(2)
        # self.tableWidget.setColumnCount(2)

        # "open file Dialog "为文件对话框的标题，第三个是打开的默认路径，第四个是文件类型过滤器

    def __init__(self, MainWindow):
        self.setupUi(MainWindow)
        # self.tableWidget.setRowCount(12)
        # self.tableWidget.setColumnCount(12)
        self.upload.clicked.connect(self.open_excel)
        self.pushButton.clicked.connect(self.popup)
        # self.tableWidget.setEditTriggers(
        # QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tplChooseBrowser.setReadOnly(True)
        self.resultLine.setReadOnly(True)
        self.templateApplyBrowser.setReadOnly(True)
        self.templateManageTable.setWordWrap(True)
        self.templateManageTable.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.historyTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.templateApplyText.textChanged.connect(self.updateTemplateText)
        # self.templateManageTable.horizontalHeader().setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
        # self.templateManageTable.horizontalHeader().setSectionResizeMode(1,QtWidgets.QHeaderView.ResizeToContents)

        self.templateManageTable.setColumnWidth(1, 100)
        self.historyTable.setColumnWidth(1,200)
        self.historyTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents
        )
        self.templateManageTable.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.login.clicked.connect(self.logInTo)
        self.logout.clicked.connect(self.logOut)
        self.pushButton.clicked.connect(self.sendData)
        self.exportFile.clicked.connect(self.export)
        self.addRow.clicked.connect(self.addRows)
        self.addCol.clicked.connect(self.addCols)
        self.deleteRow.clicked.connect(self.deleteRows)
        self.deleteCol.clicked.connect(self.deleteCols)
        self.export_table.clicked.connect(self.exportInSingle)
        self.refreshButton.clicked.connect(self.getAllTpl)
        self.addOneButton.clicked.connect(self.addOneTpl)
        self.refreshTplButtion.clicked.connect(self.refreshTpl)
        self.switchButton.clicked.connect(self.switchapi)
        self.historyRefreshButton.clicked.connect(self.getHistory)
        self.templateApplyBrowser.setText('【北理网协】')
        self.lineEdit.setFocus()
        MainWindow.showMaximized()

        self.url = URL
        self.username = UNAME
        self.password = PWORD
        self.ifLogin = False
        self.tplChosen = 0
        self.sheetncols = 0
        self.length = 0
        self.recompile = re.compile(r'#\w*#')
        self.statusLineWords = ['', '', '', '', '', '', '']
        self.tplStatusWords = ['', '', '']
        self.apiList = []
        self.apiChosen = 1  # 1:云片， 2：腾讯
        self.substite_list = []
        self.tplncals = len(self.substite_list)
        self.checkNetworkCondition()
        # 账户/网络状态   文件操作状态   保留

    def updateStatueLine(self, pos):
        res = 0  # 如果状态良好则返回值中该位置为1
        if pos & 1:
            try:
                pass
                # requests.get('http://10.0.0.55',timeout =0.5)
            except requests.exceptions.ConnectionError:
                self.statusLineWords[0] = '[无网络] 请确认有网络连接'
            else:
                try:
                    response = requests.get(self.url,timeout =0.5)
                except requests.exceptions.ConnectionError:
                    self.statusLineWords[0] = '[未正确连接服务器] 请联系管理员'
                else:
                    try:
                        self.apiList = response.json()['api']
                        self.statusLineWords[5] = '[选择服务]' + \
                            self.apiList[self.apiChosen-1]
                        self.statusLineWords[6] = ifHasUpdate(
                            response.json()['new_qt_version'])
                        string = '{"username":"'+self.username + \
                            '","password":"'+self.password+'","request_code":7}'
                        print(string)
                        response = requests.post(
                            self.url, data=string.encode())
                    except:
                        self.statusLineWords[0] = '[服务器通信异常] 连接中断'
                    else:
                        try:
                            response_dict = response.json()
                        except:
                            print(response)
                            self.statusLineWords[0] = '[服务器通信异常] 请联系管理员'
                            self.updateStatueLine(0)
                            return
                        if 'code' in response_dict and response_dict['code'] != 252:
                            words = '[通信接口有误] '+response.text
                        elif 'code' in response_dict:
                            words = '[未登录]'+'用户名或密码有误'
                        else:
                            self.ifLogin = True
                            words = '[已登录] 用户名:'+self.username
                            res |= 1
                            self.statusLineWords[2] = '[已使用]:'+str(response.json()['fee']) +\
                                ' - [已缴费]:'+str(response.json()['paid'])
                        self.statusLineWords[0] = words
        if pos & 2:
            if self.ifLogin is False:
                self.statusLineWords[1] = '[无法登出] 您还未登录'
            else:
                self.statusLineWords[1] = '已退出'
                self.statusLineWords[2] = ''
        else:
            self.statusLineWords[1] = ''

        self.statusLine.setText('\t\t'.join(self.statusLineWords))
        return res

    def updateTplStatus(self, pos):
        res = 0
        if pos & 1:
            self.tplStatusWords[0] = '[已选则id] ['+self. tplChosen+']'
            res = 1

        if pos & 2:
            if self.tplncals == self.sheetncols - 1:
                word = '[可以匹配]'
                res = 2
            else:
                word = '[无法匹配表格]   请修改表格选择其他模板'
            self.tplStatusWords[1] = word
        self.tplChooseBrowser.setText('\t\t'.join(self.tplStatusWords))
        return res

    def checkNetworkCondition(self, addition=''):
        if self.updateStatueLine(1) & 1:
            request_code = str(self.apiChosen)+'.2'
            string = '{"username":"'+self.username + \
                '","password":"'+self.password+'","request_code":'+request_code+'}'
            self.showTpl(requests.post(self.url, data=string.encode()).json())

    def logInTo(self):
        self.username, self.password = self.lineEdit.text(), self.lineEdit_2.text()
        self.statusLineWords = ['' for _ in self.statusLineWords]
        self.send_list.clear()
        self.checkNetworkCondition()

    def logOut(self):
        self.username = ''
        self.password = ''
        if self.ifLogin:
            self.statusLineWords = ['' for _ in self.statusLineWords]
            self.statusLineWords[0] = '[未登录] 已退出'
        else:
            self.statusLineWords = ['' for _ in self.statusLineWords]
            self.statusLineWords[0] = '[未登录] 您还未登录'
        self.ifLogin = False
        self.updateStatueLine(0)
        self.tplStatusWords = ['', '', '']
        self.send_list.clear()
        self.updateTplStatus(0)

    def showTpl(self, list_data):
        # length = len(list_data)

        items = map(lambda x: str(x['tpl_id'])+'\n'+x['tpl_content'],
                    filter(lambda x: x['check_status'] == 'SUCCESS', list_data))
        self.send_list.addItems(items)
        self.send_list.itemClicked.connect(self.showItem)

        # 这句不能要
        # self.send_list.setMinimumHeight(self.send_list.sizeHintForColumn(0))

    def showItem(self, QListItem):
        QListItemtext = QListItem.text()
        self.tplChosen, self.text = QListItemtext.split('\n')
        print(self.text)
        self.substite_list = re.findall(self.recompile, QListItemtext)
        self.tplncals = len(self.substite_list)
        if self.updateTplStatus(3) & 2:
            # 证明匹配
            self.tableWidget.setHorizontalHeaderLabels(
                ['手机号']+self.substite_list)
        self.tplChosen = int(self.tplChosen)

    def replaceText(self, rep_list):
        text = self.text
        for i in range(len(self.substite_list)):
            text = text.replace(self.substite_list[i], rep_list[i])
        self.updateTplStatus(2)
        return text

    def addRows(self):
        self.tableWidget.insertRow(self.length)
        self.length += 1
        self.updateTplStatus(2)
        return

    def deleteRows(self):
        self.length -= 1
        self.tableWidget.removeRow(self.length)
        self.updateTplStatus(2)
        return

    def addCols(self):
        self.tableWidget.insertColumn(self.sheetncols)
        self.sheetncols += 1
        self.updateTplStatus(2)
        return

    def deleteCols(self):
        self.sheetncols -= 1
        self.tableWidget.removeColumn(self.sheetncols)
        self.updateTplStatus(2)
        return

    def sendData(self):
        if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(None, "温馨提示", "确认发送?"):
            pass
        else:
            self.statusLineWords[4] = '[已取消] 用户取消发送短信'
            self.updateStatueLine(0)
            return

        if self.tplncals == self.sheetncols - 1:
            pass
        else:
            self.statusLineWords[4] = '[无法发送] 无法匹配表格'
            self.updateStatueLine(0)
            return
        mobile_list = []
        for i in range(self.length):
            it = self.tableWidget.item(i, 0)
            if it is None or len(it.text()) != 11:
                self.statusLineWords[4] = '[无法发送] 电话号格式错误'
                self.updateStatueLine(0)
                return
            else:
                mobile_list.append(it.text())

        data_list = []
        for i in range(self.length):
            row_list = []
            for j in range(self.sheetncols-1):
                it = self.tableWidget.item(i, j+1)
                if it is None:
                    row_list.append('')
                else:
                    row_list.append(it.text())
            data_list.append(row_list)
        print(data_list)

        if len(data_list) == 0:
            self.statusLineWords[4] = '[无法发送] 表格中没有内容'
            self.updateStatueLine(0)
            return
        elif self.tplChosen == 0:
            self.statusLineWords[4] = '[无法发送] 还未选中模板'
            self.updateStatueLine(0)
            return
        else:
            request_code = str(self.apiChosen) + '.4'
            payload = dict(username=self.username, password=self.password,
                           request_code=request_code, mobile=mobile_list,
                           content=self.text, param=data_list,
                           replace=self.substite_list)
        try:
            print(payload)
            payload = json.dumps(payload)
            print(1)
            response = requests.post(
                self.url, data=payload)
        except:
            self.statusLineWords[4] = '[网络异常] 请检查网络'
            self.updateStatueLine(0)
            return
        try:
            result_dict = response.json()
        except:
            return

        if 'code' in result_dict:  # 理论上这个问题只会在开发过程中出现，而且仅仅针对云片网
            print(result_dict)
            self.statusLineWords[4] = '[发送失败] '+result_dict['msg']
            self.updateStatueLine(0)
            return
        self.statusLineWords[4] = '[发送成功]请去结果页面查看结果'
        self.updateStatueLine(0)
        word = '[本次发送] '
        if 'total_count' in result_dict:
            word += '[total_count]:'+str(result_dict['total_count'])+' '
        if 'total_fee' in result_dict:
            word += '[total_fee]:'+str(result_dict['total_fee'])+' '
        self.resultLine.setText(word)
        presentRowCount = self.resultTable.rowCount()
        self.resultTable.setRowCount(len(result_dict['data'])+presentRowCount)
        self.resultTable.setColumnCount(3)
        self.resultTable.setHorizontalHeaderLabels(['手机号', '发送状态', '扣费'])
        # 垂直表头TODO
        print('当前列数', presentRowCount)
        for i in range(len(result_dict['data'])):
            ls = [result_dict['data'][i]['mobile'], result_dict['data']
                  [i]['msg'], result_dict['data'][i]['fee']]
            print(ls)
            for j in range(3):
                newItem = QtWidgets.QTableWidgetItem(str(ls[j]))
                self.resultTable.setItem(i+presentRowCount, j, newItem)

    def export(self):
        filename, *_ = QtWidgets.QFileDialog.getSaveFileName(
            None, "open file dialog", "output.csv", "CSV file(*.csv)")
        if filename == '':
            self.statusLineWords[3] = '[操作已取消]'
            self.updateStatueLine(0)
            return
        data_list = []
        for i in range(self.resultTable.rowCount()):
            row_list = []
            for j in range(3):
                row_list.append(self.resultTable.item(i, j).text())
            data_list.append(','.join(row_list))
        try:
            with open(filename, 'w') as file:
                file.write('\n'.join(data_list)+'\n')
        except:
            self.statusLineWords[3] = '[文件打开失败]'
        else:
            self.statusLineWords[3] = '[已储存] '+filename
        self.updateStatueLine(0)

    def exportInSingle(self):
        filename, *_ = QtWidgets.QFileDialog.getSaveFileName(
            None, "open file dialog", "output.csv", "CSV file(*.csv)")
        if filename == '':
            self.statusLineWords[3] = '[操作已取消]'
            self.updateStatueLine(0)
            return
        data_list = []
        for i in range(self.tableWidget.rowCount()):
            row_list = []
            for j in range(self.tableWidget.columnCount()):
                row_list.append(self.tableWidget.item(i, j).text())
            data_list.append(','.join(row_list))
        try:
            with open(filename, 'w') as file:
                file.write('\n'.join(data_list)+'\n')
        except:
            self.statusLineWords[3] = '[文件打开失败]'
        else:
            self.statusLineWords[3] = '[已储存] '+filename
        self.updateStatueLine(0)

    def getAllTpl(self):
        if self.updateStatueLine(1) & 1 == 0:
            return
        try:
            requests_code = str(self.apiChosen)+'.2'
            string = '{"username":"'+self.username + \
                '","password":"'+self.password+'","request_code":'+requests_code+'}'
            response = requests.post(self.url, data=string.encode())
        except:
            self.statusLineWords[4] = '[网络异常] 获取信息失败'
            self.updateStatueLine(0)
            return
        else:
            result_dict_list = response.json()
        print(result_dict_list)
        self.templateManageTable.setRowCount(len(result_dict_list))
        self.templateManageTable.setColumnCount(4)
        self.templateManageTable.setHorizontalHeaderLabels(
            ['模板id', '内容', '申请状态', '具体原因'])
        for i in range(len(result_dict_list)):
            ls = [str(result_dict_list[i]['tpl_id']), result_dict_list[i]['tpl_content'],
                  result_dict_list[i]['check_status'], result_dict_list[i]['reason']]
            for j in range(4):
                newItem = QtWidgets.QTableWidgetItem(
                    ls[j])
                self.templateManageTable.setItem(i, j, newItem)
        self.templateManageTable.setColumnWidth(1, 500)

    def updateTemplateText(self):
        self.templateApplyBrowser.setText(
            '【北理网协】'+self.templateApplyText.toPlainText())

    def addOneTpl(self):
        if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(None, "温馨提示", "确认提交模板?"):
            pass
        else:
            self.statusLineWords[4] = '[已取消] 用户取消发送模板'
            self.updateStatueLine(0)
            return

        if self.updateStatueLine(1) & 1:
            requests_code = str(self.apiChosen) + '.3'
            string = '{"username":"'+self.username + '","password":"'+self.password+'","request_code":'+requests_code+',' + \
                '"tpl_content":"'+self.templateApplyBrowser.toPlainText()+'"}'
            response = requests.post(self.url, data=string.encode())
        else:
            return
        result = response.json()
        print(result)

        if 'code' in result: # 根据接口
            self.statusLineWords[4] = '[发送失败] '+result['msg']
            self.updateStatueLine(0)
        else:
            self.statusLineWords[4] = '[发送成功] 请刷新'
            self.updateStatueLine(0)

    def refreshTpl(self):
        self.send_list.clear()
        self.checkNetworkCondition()
        self.statusLineWords[3] = '[已刷新]'
        self.updateStatueLine(0)

    def switchapi(self):
        self.apiChosen = (self.apiChosen) % len(self.apiList)+1
        self.statusLineWords[5] = '[选择服务]'+self.apiList[self.apiChosen-1]
        self.updateStatueLine(0)

    def getHistory(self):
        if self.updateStatueLine(1) & 1:
            string = '{"username":"'+self.username + '","password":"'+self.password + \
                '","request_code":6}'
            response = requests.post(self.url, data=string.encode())
            print(response.text)
        else:
            return
        result_list = response.json()
        self.historyTable.setColumnCount(7)
        self.historyTable.setHorizontalHeaderLabels(
            ['编号', '发送时间', '手机号', '参数', '费用', '详情', '回复'])
        row_count = len(result_list)
        self.historyTable.setRowCount(row_count)
        for i in range(row_count):
            for j in range(7):
                newItem = QtWidgets.QTableWidgetItem(str(result_list[i][j]))
                self.historyTable.setItem(i, j, newItem)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = my_win(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
