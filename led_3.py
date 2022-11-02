'''
#########################################
* Title: 树莓派实验
* Name:  实验三 按键检测、中断处理实验
* Author: AJ
#########################################
'''
import RPi.GPIO as GPIO
import time
import threading 
import tkinter as tk

#定义GPIO引脚
SCLK = 4
RCLK = 5
DIO = 7
LED_PINS = [4,5,7]
GPIO.setmode(GPIO.BCM) #设置引脚编号为BCM编号方式

for led_pin in LED_PINS: #将这些GPIO引脚设置为输出
    GPIO.setup(led_pin,GPIO.OUT)
LED_Library = [0xC0, 0xF9, 0xA4,0xB0,0x99,0x92,0x82,
               0xF8,0x80,0x90,0x8C,0xBF,0xC6,0xA1,0x86,0x8E,0xbf] #定义字模

'''
* 函数名称：Show(i_data)
* 功能：将i_data表示的数值，显示在4位数码管做上。
* 参数含义：
        i_data：要显示在数码管上的数值
'''
def Show(i_data):
    #提取i_data数值的每一位上的值
    while i_data > 10000:
        i_data = i_data - 10000 #将数值限制在10000以下
    if(i_data >= 1000):
        i_show1 = i_data//1000 #提取千位的值，存在i_show1中
        i_data = i_data - i_show1 * 1000 #减去千位
    else:
        i_show1 = 0
    if(i_data >= 100): #提取百位值，存在i_show2中
        i_show2 = i_data//100 #减去百位
        i_data -= 100 * i_show2
    else:
        i_show2 = 0
    if(i_data >= 10):
        i_show3 = i_data//10 #提取十位值，存在i_show3中
        i_data -= 10*i_show3 #减去十位
    else:
        i_show3 = 0
    i_show4 = i_data #提取个位值，存在i_show4中
    LED4_Display(i_show1,0x08) #将千位值写入4位数码管模块的从左往右的第一位
    LED4_Display(i_show2,0x04) #将百位值写入4位数码管模块的从左往右的第二位
    LED4_Display(i_show3,0x02) #将十位值写入4位数码管模块的从左往右的第三位
    LED4_Display(i_show4,0x01) #将个位值写入4位数码管模块的从左往右的第四位

'''
* 函数名称：LED4_Display(i_index,hx_location)
* 功能：将i_index数字对应的数模，输入到4位数码管的hx_location个位置上显示出来。
* 参数含义：
        i_index：在该位要显示的数字
        hx_location: 表示4位数码管的某一位
'''
def LED4_Display(i_index,hx_location):
    LED_OUT(LED_Library[i_index]) #将要显示的字模型，输入到指定的4位数码管上
    LED_OUT(hx_location) #将位地址，输入到指定的4位数码管上
    GPIO.output(RCLK,GPIO.LOW) #字模和地址都通过DIO接口输出后，第一个4位数码管的接收时钟RCLK发出一个跳变信号，表示输出完成
    GPIO.output(RCLK,GPIO.HIGH) #即先低电平，再高电平

'''
* 函数名称：LED_OUT(X)
* 功能：将数据X输入到4位数码管模块上
* 参数含义：
        X: 一个字节的数据X，可以是字模数据，也可以是地址数据
''' 
def LED_OUT(X):
    for i in range(0,8): #一个字节是八位，循环8次将每一位数据通过DIO口输出到显示模块
        if(X&0x80): #如果X最高位是1
            GPIO.output(DIO,GPIO.HIGH) #则给高电平信号
        else:
            GPIO.output(DIO,GPIO.LOW) #低电平
        GPIO.output(SCLK,GPIO.LOW) #每一位数据输出后，都要给串行时钟一个跳变信号，（先低电平，后高电平）
        GPIO.output(SCLK,GPIO.HIGH)
        X<<=1 #X数据向左移一位，即准备读取下一位的数据

KEY1 = 3 #设置GPIO引脚，对应按钮模块的输入引脚K1
KEY2 = 17 #对应K2
KEY3 = 27 #对应K3
value = 10 #全局变量值

'''
* 函数名称：key_callback(channel)
* 功能：定义中断响应函数，函数中是识别按键，做出相应的加、减、清零等操作。
* 参数含义：
        channel: 引脚信号
''' 
def key_callback(channel):
    global value,text1 #全局变量value值,和窗口模块的text组件
    if(channel == 3 and value > -1): #接红色按钮，对应加法功能
        value = value + 1
    if(channel == 17): #接黄色按钮，对应减法功能
        value = value - 1
    if(channel == 27 and value < 9999): #接绿色按钮，对应清零功能
        value = 0
    #将最新的value值更新在窗口模块的text1组件中
    text1.delete(0.0,tk.END)
    text1.insert(tk.INSERT,value)
    text1.update()

'''
* 函数名称：GPIO_init()
* 功能：初始化GPIO设置，如设置GPIO编号方式、设置引脚模式、注册中断事件、绑定中断响应函数
* 参数含义：
''' 
def GPIO_init():
    GPIO.setmode(GPIO.BCM) #设置GPIO编号方式
    #设置KEY1、2、3为输入模式、上拉模式
    GPIO.setup(KEY1, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(KEY2, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(KEY3, GPIO.IN, GPIO.PUD_UP)
    #给三个引脚注册中断事件，指定下降沿，读取信号延迟事件为200毫秒
    GPIO.add_event_detect(KEY1, GPIO.FALLING, bouncetime = 200)
    GPIO.add_event_detect(KEY2, GPIO.FALLING, bouncetime = 200)
    GPIO.add_event_detect(KEY3, GPIO.FALLING, bouncetime = 200)
    #给三个引脚绑定中断响应函数
    GPIO.add_event_callback(KEY1,callback = key_callback)
    GPIO.add_event_callback(KEY2,callback = key_callback)
    GPIO.add_event_callback(KEY3,callback = key_callback)

'''
* 函数名称：thread1_show()
* 功能：线程1，在数码管上动态显示全局变量value值
* 参数含义：
''' 
def thread1_show():
    while True:
        Show(value)


lock = threading.Lock() #设置线程锁
'''
* 函数名称：thread2_tk()
* 功能：线程2，绘制窗口界面，并循环显示界面内容。
* 参数含义：
''' 
def thread2_tk():
    global text1,bt1,bt2,bt3,windows #全局变量的组件和窗口句柄
    if lock.acquire(1): #判断是否能获取到锁，能得话执行下面代码
        #这样在绘制过程中，这些组件内容不会别其他线程所改变
        windows = tk.Tk() #窗口句柄
        windows.geometry('500x500')  ## 规定窗口大小500*500像素
        windows.resizable(False, False)  ## 规定窗口不可缩放
        lab1 = tk.Label(windows, text='value数值：', height=1, width=15, fg='black')
        lab1.grid(row=0, column=0, padx=5, pady=5)
        text1 = tk.Text(windows,width=15,height=1)
        text1.insert(tk.INSERT,value)
        text1.grid(row=0,column=1,padx=10,pady=10)
        bt1 = tk.Button(windows,bg = "red",text = "按键输出值：1", height = 2, width = 15)
        bt1.grid(row=1, column=0, padx=5,pady=5)
        bt2 = tk.Button(windows,bg = "yellow",text = "按键输出值：1", height = 2, width = 15)
        bt2.grid(row=1, column=1, padx=5,pady=5)
        bt3 = tk.Button(windows,bg = "green",text = "按键输出值：1", height = 2, width = 15)
        bt3.grid(row=1, column=2, padx=5,pady=5)
        lock.release #释放锁
    windows.mainloop() #循环显示界面内容

#下面是用三个线程分别监听三个按钮的状态
'''
* 函数名称：thread3_readKey1()
* 功能：线程3，用input(channel)函数读取引脚信号，监听红色按钮信号
* 参数含义：
''' 
def thread3_readKey1():
    global bt1 #全局参数，button组件
    while True:
        time.sleep(0.05)
        if GPIO.input(KEY1) == 0: #当按钮按下输出低电平信号
            print("add")
            bt1["state"] = "active" 
            bt1["text"] = "按键输出值：0" #动态更改tk窗口中的内容，此时为按钮按下的状态
            while GPIO.input(KEY1) == 0: 
                time.sleep(0.01) #延时防抖动
            #print("RED KEY UP!")
            bt1["state"] = "normal" 
            bt1["text"] = "按键输出值：1" #恢复按钮的状态

'''
* 函数名称：thread4_readKey2()
* 功能：线程4，用input(channel)函数读取引脚信号，监听黄色按钮信号
* 参数含义：
''' 
def thread4_readKey2():
    global bt2 #全局参数，button组件
    while True:
        time.sleep(0.05)
        if GPIO.input(KEY2) == 0: #当按钮按下输出低电平信号
            print("subtract")
            bt2["state"] = "active"
            bt2["text"] = "按键输出值：0" #动态更改tk窗口中的内容，此时为按钮按下的状态
            while GPIO.input(KEY2) == 0:
                time.sleep(0.01) #延时防抖动
            #print("yellow KEY UP!")
            bt2["state"] = "normal"
            bt2["text"] = "按键输出值：1" #恢复按钮的状态

'''
* 函数名称：thread5_readKey3()
* 功能：线程5，用input(channel)函数读取引脚信号，监听红色按钮信号
* 参数含义：
'''        
def thread5_readKey3():
    global bt3 #全局参数，button组件
    while True:
        time.sleep(0.05)
        if GPIO.input(KEY3) == 0: #当按钮按下输出低电平信号
            print("clear")
            bt3["state"] = "active"
            bt3["text"] = "按键输出值：0" #动态更改tk窗口中的内容，此时为按钮按下的状态
            while GPIO.input(KEY3) == 0:
                time.sleep(0.01) #延时防抖动
            #print("green KEY UP!")
            bt3["state"] = "normal"
            bt3["text"] = "按键输出值：1" #恢复按钮的状态

if __name__ == "__main__":
    GPIO_init() #GPIO口初始化
    #设置五个线程：数码管显示、桌面tk窗口循环显示、三个按钮监听线程
    thread1 = threading.Thread(target = thread1_show,args = ())
    thread2 = threading.Thread(target = thread2_tk,args = ())
    thread3 = threading.Thread(target = thread3_readKey1,args = ())
    thread4 = threading.Thread(target = thread4_readKey2,args = ())
    thread5 = threading.Thread(target = thread5_readKey3,args = ())
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
