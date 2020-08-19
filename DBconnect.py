# -- coding: utf-8 --
import mysql.connector


class MysqlHelp(object):
    # 构造
    def __init__(self, host, user, passwd, db, port=3306):
        self.host = host
        self.user = user
        self.port = port
        self.passwd = passwd
        self.db = db

    # 创建连接
    def open_coon(self):
        self.coon = mysql.connector.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        self.cursor = self.coon.cursor()

    # 关闭连接
    def close(self):
        self.cursor.close()
        self.coon.cursor()

    # 调用语句
    def insert_delete_update(self, sql, params=[]):
        try:
            self.open_coon()
            self.cursor.execute(sql, params)
            print("OK")
            self.coon.commit()
            self.close()
        except Exception as erorr:
            print(erorr)

    # 查询 接收全部的返回结果行

    def select_fetchall(self, sql, params=[]):
        try:
            self.open_coon()
            self.cursor.execute(sql, params)
            results = self.cursor.fetchall()
            self.coon.commit()
            self.close()
            return results
        except Exception as erorr:
            print(erorr)

