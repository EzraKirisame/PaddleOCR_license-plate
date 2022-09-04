import time
from multiprocessing import Process, Queue
from paddleocr import PaddleOCR, draw_ocr
import cv2
import pickle
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy
import easygui
import pymysql

# 模型路径下必须含有model和params文件
ocr = PaddleOCR(use_angle_cls=True,
                use_gpu=False)  # det_model_dir='{your_det_model_dir}', rec_model_dir='{your_rec_model_dir}', rec_char_dict_path='{your_rec_char_dict_path}', cls_model_dir='{your_cls_model_dir}', use_angle_cls=True
img_path = 'PaddleOCR/doc/result/result.jpg'
global result
global frame

def getImformation(name):
    # global frame,result
    while (True):
        try:
            frame = numpy.load('frameData.npy')
            result = ocr.ocr(frame, cls=True)
            pickle.dump(result, open('resultData.json', 'wb'))
            print(type(result))
            time.sleep(3)
        except:
            # i = 1
            time.sleep(3)

def showImage():
    cap = cv2.VideoCapture(0)
    p = Process(target=getImformation, args=("Process1",))
    p.start()

    conn = pymysql.connect(host='localhost', user='root', password='123456', charset='utf8mb4', database='garage')
    print('连接数据库成功')

    while (True): #开始循环检测
        ret, frame = cap.read()
        #cv2.imshow(frame)
        if ret:
            numpy.save('frameData', frame)
            with open('resultData.json', 'rb') as f:
                try:
                    result = pickle.load(f)
                except:
                    result = []
            for line in result:
                print( )
                number = line[-1][0]
                fin = easygui.buttonbox(msg = number,choices = ('确认车牌','取消录入'),title = "当前车牌号")
                while True:
                    if fin == "确认车牌":
                        judgment = "select exists (SELECT * from  license_plate  where id = '%s');"%(number)    #查看数据库是否存在该车牌
                        cursor = conn.cursor()
                        cursor.execute(judgment)  # 执行SQL语句
                        flag = cursor.fetchall()[0][0]
                        #print(flag)
                        conn.commit()  # 提交到数据库
                        cursor.close()  # 关闭游标
                        if(flag==0):#此车牌第一次进入该车库
                            print('新车牌'+number)
                            print("车牌数据录入中")
                            #easygui.msgbox("车牌数据录入中", title="车辆数据录入结果")
                            sql = "INSERT INTO license_plate (id,state,total,level,last_time) " \
                                  "VALUES('%s',1,1,1,NOW());"%(number)                                          #录入id
                            try:
                                cursor = conn.cursor()
                                cursor.execute(sql)  # 执行SQL语句
                                print("车牌id录入成功,全部数据初始化成功")
                                #easygui.msgbox("车牌id录入成功,全部数据初始化成功!", ok_button="继续检测", title = "车辆数据录入结果")
                                conn.commit()  # 提交到数据库
                                cursor.close() # 关闭游标
                            except:
                                # 如果发生错误则回滚
                                conn.rollback()
                                print("车牌数据录入失败，请手动更改数据库或重新录入")
                                easygui.msgbox("车牌数据录入失败，请手动更改数据库或重新录入", ok_button="继续检测", title="车辆数据录入结果")
                                # 关闭游标
                                cursor.close()
                                break
                            break
                        else:
                            print('更新车牌'+number)
                            print("车牌数据更新中")
                            sql6 = "update license_plate set total = total+1 where id = '%s' and state = 0;" % (number)     #更新总次数(进商场加1，出商场不计入)
                            sql7 = "update license_plate set state = ABS(state-1) where id = '%s';"%(number)                #更新在场状态
                            sql8 = "update license_plate set last_time = NOW() where id = '%s';"%(number)                   #更新最后时间
                            vip1 = "SELECT total from license_plate  where id = '%s';"%(number)                             #检查VIP更新
                            state1 = "SELECT state from license_plate  where id = '%s';"%(number)                           #检查在场状态
                            vip2 = "update license_plate set level = 2 where id = '%s';" % (number)                         #VIP2
                            vip3 = "update license_plate set level = 3 where id = '%s';" % (number)                         #VIP3
                            vip4 = "update license_plate set level = 4 where id = '%s';" % (number)                         #VIP4
                            vip5 = "update license_plate set level = 5 where id = '%s';" % (number)                         #VIP5
                            try:
                                cursor = conn.cursor()
                                cursor.execute(sql6)  # 执行SQL语句
                                print("更新在场状态成功")
                                cursor.execute(sql7)  # 执行SQL语句
                                print("更新总次数成功")
                                cursor.execute(sql8)  # 执行SQL语句
                                print("更新最后时间成功")
                                cursor.execute(vip1)  # 执行SQL语句
                                print("检查vip更新")
                                vipflag = cursor.fetchall()[0][0]
                                cursor.execute(state1)  # 执行SQL语句
                                print("检查在场状态")
                                stateflag = cursor.fetchall()[0][0]
                                if(vipflag==20 and stateflag==1):
                                    cursor.execute(vip2)  # 执行SQL语句
                                    print(number+"车主升级为VIP2！")
                                elif (vipflag==30 and stateflag==1):
                                    cursor.execute(vip3)  # 执行SQL语句
                                    print(number + "车主升级为VIP3！")
                                elif (vipflag==40 and stateflag==1):
                                    cursor.execute(vip4)  # 执行SQL语句
                                    print(number + "车主升级为VIP4！")
                                elif (vipflag==50 and stateflag==1):
                                    cursor.execute(vip5)  # 执行SQL语句
                                    print(number + "车主升级为VIP5！")
                                #print(vipflag)
                                conn.commit()  # 提交到数据库
                                cursor.close() # 关闭游标
                            except:
                                # 如果发生错误则回滚
                                conn.rollback()
                                print("车牌数据更新失败，请手动更新或取消")
                                # 关闭游标
                                cursor.close()
                                break
                            break
                    else:
                        break
                draw_rectangle(frame, line)
                # cv2.rectangle(frame, (int(line[0][0][0]-2), int(line[0][0][1]-2)), (int(line[0][2][0]+2), int(line[0][2][1]+2)),
                #               (0, 255, 0), 3)
                frame = cv2ImgAddText(frame, line[1][0], int(line[0][0][0] + 2), int(line[0][0][1] + 2), (255, 0, 0),
                                      20)
            cv2.imshow("3秒实时检测", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # 关闭连接
                conn.close()
                print('数据库断开连接')
                break
        time.sleep(3)

def draw_rectangle(frame, pos):
    cv2.line(frame, (int(pos[0][0][0]), int(pos[0][0][1])), (int(pos[0][1][0]), int(pos[0][1][1])), (0, 255, 0), 1, 4)
    cv2.line(frame, (int(pos[0][1][0]), int(pos[0][1][1])), (int(pos[0][2][0]), int(pos[0][2][1])), (0, 255, 0), 1, 4)
    cv2.line(frame, (int(pos[0][2][0]), int(pos[0][2][1])), (int(pos[0][3][0]), int(pos[0][3][1])), (0, 255, 0), 1, 4)
    cv2.line(frame, (int(pos[0][3][0]), int(pos[0][3][1])), (int(pos[0][0][0]), int(pos[0][0][1])), (0, 255, 0), 1, 4)

def cv2ImgAddText(img, text, left, top, textColor, textSize):
    if (isinstance(img, numpy.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    #cv2.imshow(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "font/simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


if __name__ == "__main__":
    showImage()

