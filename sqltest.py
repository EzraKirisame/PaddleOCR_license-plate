#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pymysql

# 查询所有字段
def list_col(tabls_name):
    db = pymysql.connect(host='localhost',user='root',password='123456',charset='utf8mb4',database='garage')
    cursor = db.cursor()
    cursor.execute("select * from %s" % tabls_name)
    col_name_list = [tuple[0] for tuple in cursor.description]
    db.close()
    return col_name_list

# 列出所有的表
def list_table():
    db = pymysql.connect(host='localhost',user='root',password='123456',charset='utf8mb4',database='garage')
    cursor = db.cursor()
    cursor.execute("show tables")
    table_list = [tuple[0] for tuple in cursor.fetchall()]
    db.close()
    return table_list

tables = list_table() # 获取所有表，返回的是一个可迭代对象
print(tables)

for table in tables:
    col_names = list_col(table)
    print(col_names) # 输出所有字段名
