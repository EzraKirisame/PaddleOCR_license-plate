import pymysql
# 创建连接
conn = pymysql.connect(host='localhost',user='root',password='123456',charset='utf8mb4',database='garage')
# 创建游标
cursor = conn.cursor()

# 创建数据库的sql(如 看·                果数据库存在就不创建，防止异常)
#sql = "CREATE DATABASE IF NOT EXISTS db_name"
# 执行创建数据库的sql
#cursor.execute(sql)

# 创建表
sql_2 = '''CREATE TABLE `license_plate` (
  `id` varchar(255)  NOT NULL,          #车牌号
  `total` INT DEFAULT NULL,                 #总次数
  `state` INT DEFAULT NULL,                 #在车库的状态
  `level` INT DEFAULT NULL,                 #贵宾等级
  `last_time` datetime DEFAULT NULL,    #最后离开时间
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''
cursor.execute(sql_2)