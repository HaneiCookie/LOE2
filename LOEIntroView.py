import tkinter as tk

import mLightDevice
import os
import re
import serial
import time
from datetime import datetime
import pygame
import mAppDefine
import socket
import json
import threading
from datetime import datetime
from PIL import Image, ImageTk

class LOEIntroView(tk.Frame):

    device_01 = None

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)

        self.image = Image.open(mAppDefine.root_path + mAppDefine.intro_png)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        #self.canvas.pack(fill="both", expand=True)
        self.canvas.place(x=0,y=0)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.deductionTime = 0

        self.parentView = parent

        options = ["0", "5", "10","15","20","25","30","35","40","45","50"]
        # 기본 선택 옵션
        selected_option = tk.StringVar(self)
        selected_option.set(options[0])  # 기본 선택 옵션 설정
        
        # 드롭다운 메뉴 생성
        option_menu = tk.OptionMenu(self, selected_option, *options, command=self.on_select_time)
        option_menu.pack()

        self.L01_Status = tk.Label(self,text='L01 wait',font=(mAppDefine.common_font,20))
        self.L01_Status.place(x=50, y=400)
        self.L02_Status = tk.Label(self,text='L02 wait',font=(mAppDefine.common_font,20))
        self.L02_Status.place(x=50, y=500)
        self.L03_Status = tk.Label(self,text='L03 wait',font=(mAppDefine.common_font,20))
        self.L03_Status.place(x=50, y=600)
        self.L04_Status = tk.Label(self,text='L04 wait',font=(mAppDefine.common_font,20))
        self.L04_Status.place(x=50, y=700)
        self.L05_Status = tk.Label(self,text='L05 wait',font=(mAppDefine.common_font,20))
        self.L05_Status.place(x=50, y=800)
        self.L06_Status = tk.Label(self,text='L06 wait',font=(mAppDefine.common_font,20))
        self.L06_Status.place(x=50, y=900)

        self.L01Button = tk.Button(self, width = 4, height = 1, text = 'L01', font=(mAppDefine.common_font,30), command=self.onClickL01Button, bg = 'white')
        self.L01Button.place(x=50,y=200)
        self.L02Button = tk.Button(self, width = 4, height = 1, text = 'L02', font=(mAppDefine.common_font,30), command=self.onClickL02Button, bg = 'white')
        self.L02Button.place(x=200,y=200)
        self.L03Button = tk.Button(self, width = 4, height = 1, text = 'L03', font=(mAppDefine.common_font,30), command=self.onClickL03Button, bg = 'white')
        self.L03Button.place(x=350,y=200)
        self.L04Button = tk.Button(self, width = 4, height = 1, text = 'L04', font=(mAppDefine.common_font,30), command=self.onClickL04Button, bg = 'white')
        self.L04Button.place(x=500,y=200)
        self.L05Button = tk.Button(self, width = 4, height = 1, text = 'L05', font=(mAppDefine.common_font,30), command=self.onClickL05Button, bg = 'white')
        self.L05Button.place(x=650,y=200)
        self.L06Button = tk.Button(self, width = 4, height = 1, text = 'L06', font=(mAppDefine.common_font,30), command=self.onClickL06Button, bg = 'white')
        self.L06Button.place(x=800,y=200)

        self.device_01 = None
        self.device_02 = None
        self.device_03 = None
        self.device_04 = None
        self.device_05 = None
        self.device_06 = None

        self.inputLayerEntry = tk.Entry(self,font=(mAppDefine.common_font,120), width = 5)
        self.inputLayerEntry.place(relx = mAppDefine.layerInputButton_rel_x, rely = mAppDefine.layerInputButton_rel_y)
        self.inputLayerEntry.bind("<Return>", self.onEnterEntry)

        self.setFlag = False
        self.rdFlag = False
        self.startFlag = False

        #self.button2 = tk.Button(self, width = 5, height = 1, text="NEXT", font = (mAppDefine.common_font,50), command=lambda: self.onClickNextBtn(parent), fg="white",bg=mAppDefine.nextButtonColor)
        #self.button2.place(relx = mAppDefine.nextButton_rel_x, rely = mAppDefine.nextButton_rel_y)

        #self.readyButton = tk.Button(self, width = 5, height = 1, text="READY", font = (mAppDefine.common_font,40), command=lambda: self.onClickReadyBtn(), fg="white",bg=mAppDefine.nextButtonColor)
        #self.readyButton.place(relx = mAppDefine.nextButton_rel_x, rely = mAppDefine.nextButton_rel_y-0.2)

    def init_server(self):
        self.host = '192.168.219.200'
        self.port = mAppDefine.portNumber

        self.server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host,self.port))

    def show_debug_text(self,target,text):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        target.config(text=time_str+" "+text)

    def init_light_device(self):
        print("ip1 : ", mAppDefine.light_01)
        self.device_01 = mLightDevice.Device("L_01",mAppDefine.light_01)
        self.device_01.start_keepalive(45)
        self.show_debug_text(self.L01_Status,self.device_01.connect())

        print("ip2 : ", mAppDefine.light_02)
        self.device_02 = mLightDevice.Device("L_02",mAppDefine.light_02)
        self.device_02.start_keepalive(45)
        self.show_debug_text(self.L02_Status,self.device_02.connect())
  
        print("ip3 : ", mAppDefine.light_03)
        self.device_03 = mLightDevice.Device("L_03",mAppDefine.light_03)
        self.device_03.start_keepalive(45)
        self.show_debug_text(self.L03_Status,self.device_03.connect())
        
        print("ip4 : ", mAppDefine.light_04)
        self.device_04 = mLightDevice.Device("L_04",mAppDefine.light_04)
        self.device_04.start_keepalive(45)
        self.show_debug_text(self.L04_Status,self.device_04.connect())

        print("ip5 : ", mAppDefine.light_05)
        self.device_05 = mLightDevice.Device("L_05",mAppDefine.light_05)
        self.device_05.start_keepalive(45)
        self.show_debug_text(self.L05_Status,self.device_05.connect())

        print("ip6 : ", mAppDefine.light_06)
        self.device_06 = mLightDevice.Device("L_06",mAppDefine.light_06)
        self.device_06.start_keepalive(45)
        self.show_debug_text(self.L06_Status,self.device_06.connect())

    def find_device(self,mac_address):        
        # MAC 주소 포맷 통일 (소문자, 콜론 기준)
        normalized_mac = mac_address.lower().replace(":", "-")
        #print(normalized_mac)
        # ARP 테이블 출력
        arp_output = os.popen("arp -a").read()
        #print(arp_output)
        
        # 각 줄을 확인
        for line in arp_output.splitlines():
            if normalized_mac in line.lower():
                #print(line.lower())
                # IP 주소 추출
                match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
                #print(match)
                if match:
                    return match.group()
        return None

    def onClickL01Button(self):
        if(self.device_01.lightStatus == True):
            self.device_01.turnOff()
        else:
            self.device_01.turnOn()
    
    def onClickL02Button(self):
        if(self.device_02.lightStatus == True):
            self.device_02.turnOff()
        else:
            self.device_02.turnOn()
    
    def onClickL03Button(self):
        if(self.device_03.lightStatus == True):
            self.device_03.turnOff()
        else:
            self.device_03.turnOn()

    def onClickL04Button(self):
        if(self.device_04.lightStatus == True):
            self.device_04.turnOff()
        else:
            self.device_04.turnOn()

    def onClickL05Button(self):
        if(self.device_05.lightStatus == True):
            self.device_05.turnOff()
        else:
            self.device_05.turnOn()

    def onClickL06Button(self):
        if(self.device_06.lightStatus == True):
            self.device_06.turnOff()
        else:
            self.device_06.turnOn()

    def stopBGM(self):
        self.bgSound.stop()

    def on_select_time(self,value):
       self.deductionTime = int(value)
       print(self.deductionTime)

    def onEnterEntry(self,event):
        inputString = self.inputLayerEntry.get().upper()
        if (inputString == '시작'): #mAppDefine.startCode:
            #if(self.setFlag == True and self.rdFlag == True):
                mAppDefine.timeLimitMin -= self.deductionTime
                #print("nextBtn")
                #print(mAppDefine.timeLimitMin)
                self.parentView.SetStartTime(mAppDefine.timeLimitMin*mAppDefine.MIN_TO_SEC)
                mAppDefine.timerFlag = True
                self.parentView.start_timer()

                connect_handler = threading.Thread(target=self.sendStartSignalOffice,daemon=True)
                connect_handler.start()

                self.parentView.SetGameView()
                self.parentView.show_frame(mAppDefine.View.LOEGameView)
        elif (inputString == "ㅅㅌ"):
            self.setFlag = True 
            self.init_light_device()
            self.device_01.turnOn()
            self.device_02.turnOn()
            self.device_03.turnOn()
            self.device_04.turnOn()
            self.device_05.turnOn()
            self.device_06.turnOn()
            self.parentView.SetBGM()
            self.inputLayerEntry.delete(0,tk.END)
        elif (inputString == "ㄹㄷ") :
            self.rdFlag = True
            self.L01_Status.place_forget()
            self.L02_Status.place_forget()
            self.L03_Status.place_forget()
            self.L04_Status.place_forget()
            self.L05_Status.place_forget()
            self.L06_Status.place_forget()

            self.L01Button.place_forget()
            self.L02Button.place_forget()
            self.L03Button.place_forget()
            self.L04Button.place_forget()
            self.L05Button.place_forget()
            self.L06Button.place_forget()

            self.device_01.turnOff()
            self.device_02.turnOff()
            self.device_03.turnOff()
            self.device_04.turnOff()
            self.device_05.turnOff()
            self.device_06.turnOff()

            self.inputLayerEntry.delete(0,tk.END)
        else:
            print("onClickNextBtn error : ",inputString)
    
    def sendStartSignalOffice(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((mAppDefine.officeServerIP, mAppDefine.officeServerPort))  # 서버의 호스트와 포트에 연결

        remainTime = mAppDefine.timeLimitMin*mAppDefine.MIN_TO_SEC*mAppDefine.ONE_MIL_SEC
        # 서버로 데이터 전송
        data_to_send = {
            "themeType" : mAppDefine.themeType,
            "codeType" : mAppDefine.codeType_START,
            "msg" : remainTime
        }
        json_data = json.dumps(data_to_send)
        client_socket.sendall(json_data.encode('utf-8'))
        client_socket.close()

    def updateFrame(self):
        print("")
    