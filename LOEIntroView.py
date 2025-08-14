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

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)

        self.image = Image.open(mAppDefine.root_path + mAppDefine.intro_png)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        #self.canvas.pack(fill="both", expand=True)
        self.canvas.place(x=0,y=0)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.deductionTime = 0

        options = ["0", "5", "10","15","20","25","30","35","40","45","50"]
        # 기본 선택 옵션
        selected_option = tk.StringVar(self)
        selected_option.set(options[0])  # 기본 선택 옵션 설정
        
        # 드롭다운 메뉴 생성
        option_menu = tk.OptionMenu(self, selected_option, *options, command=self.on_select_time)
        option_menu.pack()

        self.topLightStatus = tk.Label(self,text='top wait',font=(mAppDefine.common_font,20))
        self.topLightStatus.place(x=50, y=400)
        self.midLightStatus = tk.Label(self,text='mid wait',font=(mAppDefine.common_font,20))
        self.midLightStatus.place(x=50, y=500)
        self.botLightStatus = tk.Label(self,text='bot wait',font=(mAppDefine.common_font,20))
        self.botLightStatus.place(x=50, y=600)

        self.laserStatus = tk.Label(self,text='laser wait',font=(mAppDefine.common_font,20))
        self.laserStatus.place(x=50, y=700)

        self.magneticStatus = tk.Label(self,text='magnetic wait',font=(mAppDefine.common_font,20))
        self.magneticStatus.place(x=50, y=800)

        self.topLightButton = tk.Button(self, width = 4, height = 1, text = 'top', font=(mAppDefine.common_font,30), command=self.onClickTopLightButton, bg = 'white')
        self.topLightButton.place(x=50,y=200)
        self.midLightButton = tk.Button(self, width = 4, height = 1, text = 'mid', font=(mAppDefine.common_font,30), command=self.onClickMidLightButton, bg = 'white')
        self.midLightButton.place(x=200,y=200)
        self.botLightButton = tk.Button(self, width = 4, height = 1, text = 'bot', font=(mAppDefine.common_font,30), command=self.onClickBotLightButton, bg = 'white')
        self.botLightButton.place(x=350,y=200)

        self.device_01 = None
        self.device_02 = None
        self.device_03 = None

        self.inputLayerEntry = tk.Entry(self,font=(mAppDefine.common_font,120), width = 5)
        self.inputLayerEntry.place(relx = mAppDefine.layerInputButton_rel_x, rely = mAppDefine.layerInputButton_rel_y)

        self.button2 = tk.Button(self, width = 5, height = 1, text="NEXT", font = (mAppDefine.common_font,50), command=lambda: self.onClickNextBtn(parent), fg="white",bg=mAppDefine.nextButtonColor)
        self.button2.place(relx = mAppDefine.nextButton_rel_x, rely = mAppDefine.nextButton_rel_y)

        self.readyButton = tk.Button(self, width = 5, height = 1, text="READY", font = (mAppDefine.common_font,40), command=lambda: self.onClickReadyBtn(), fg="white",bg=mAppDefine.nextButtonColor)
        self.readyButton.place(relx = mAppDefine.nextButton_rel_x, rely = mAppDefine.nextButton_rel_y-0.2)

    def onClickReadyBtn(self):
        #self.init_light_device()
        #self.init_serial_port()

        self.init_server()
        self.server_socket.listen(1)
        print('서버 대기중..')
        self.server_handler = threading.Thread(target=self.HandleServer,daemon=True)
        print('h1')
        self.server_handler.start()


        self.init_remote_port()

        #self.ser_handler = threading.Thread(target=self.StartSerial)
        #self.ser_handler.start()

    def HandleServer(self):
        print('s0')
        self.show_debug_text(self.magneticStatus,"MAG_01 wait")
        while True:
            print('s0.5')
            client_socket, addr = self.server_socket.accept()
            print('s1')

            self.client_handler = threading.Thread(target=self.HandleClient,args=(client_socket,),daemon=True)
            print('s2 클라이언트 연결 완료 : ', addr)
            self.client_handler.start() 
    
    def HandleClient(self,client_socket):
        print('s3')
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            #print('data :', data)
            if not data:
                break    
            try:
                rcv_json = json.loads(data)
                print('rcv data :', rcv_json)
                self.ParseJsonData(rcv_json)                
                response_data = "pyend"
                print('rcv data 22')
                #client_socket.sendall(response_data.encode('utf-8'))
                print('rcv data 33')
            except json.JSONDecodeError as e:
                print('json decode error : ', e)

    def ParseJsonData(self,_jsonData):
        themeType = _jsonData['themeType']
        codeType = _jsonData['codeType']
        msg = _jsonData['msg']

        if(themeType != mAppDefine.themeTypeString_LOE):
            return
        
        if(codeType == mAppDefine.codeTypeString_MAGNETIC):
            self.show_debug_text(self.magneticStatus,msg)  

    def init_server(self):
        self.host = '192.168.35.195'
        self.port = mAppDefine.portNumber

        self.server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host,self.port))

    def init_remote_port(self):
        return


    def StartSerial(self):
        while(True):
            if(self.ser1.in_waiting > 0):
                arduino_data = self.ser1.readline().decode('utf-8').rstrip()
                print('laser data : ', arduino_data)
                self.show_debug_text(self.laserStatus,arduino_data)
                self.processInput(arduino_data)

    def processInput(self,inputData):
        print('input data : ' , inputData)


    def init_serial_port(self):
        self.file_path1 = mAppDefine.root_path + mAppDefine.LOELaserPortFilePath  # 실제 파일 경로에 따라 변경
        with open(self.file_path1, 'r') as file:
            content = file.read()
        print(content)

        self.arduino_port = content
        # 시리얼 통신 속도 설정 (아두이노의 Serial.begin 값과 일치해야 함)
        self.baud_rate = 9600
        # 시리얼 포트 열기
        self.ser1 = serial.Serial(self.arduino_port, self.baud_rate)
        time.sleep(2)

        self.show_debug_text(self.laserStatus,'laser sync')
        #self.laserStatus.config(text='laser sync')

    def show_debug_text(self,target,text):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        target.config(text=time_str+" "+text)

    def init_light_device(self):
        ip1 = self.find_device(mAppDefine.light_top_01)
        print("ip1 : ", ip1)
        self.device_01 = mLightDevice.Device("TOP_01",ip1)
        self.show_debug_text(self.topLightStatus,self.device_01.connect())

        ip2 = self.find_device(mAppDefine.light_mid_01)       
        print("ip2 : ", ip2)
        self.device_02 = mLightDevice.Device("MID_01",ip2)
        self.show_debug_text(self.midLightStatus,self.device_02.connect())

        ip3 = self.find_device(mAppDefine.light_bot_01)       
        print("ip3 : ", ip3)
        self.device_03 = mLightDevice.Device("BOT_01",ip3)
        self.show_debug_text(self.botLightStatus,self.device_03.connect())
        

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

    def onClickTopLightButton(self):
        if(self.device_01.lightStatus == True):
            self.device_01.turnOff()
        else:
            self.device_01.turnOn()
    
    def onClickMidLightButton(self):
        if(self.device_02.lightStatus == True):
            self.device_02.turnOff()
        else:
            self.device_02.turnOn()
    
    def onClickBotLightButton(self):
        if(self.device_03.lightStatus == True):
            self.device_03.turnOff()
        else:
            self.device_03.turnOn()

    def stopBGM(self):
        self.bgSound.stop()

    def on_select_time(self,value):
       self.deductionTime = int(value)
       print(self.deductionTime)

    def onClickNextBtn(self,parent):
        inputString = self.inputLayerEntry.get().upper()
        if inputString == 'S': #mAppDefine.startCode:       
            mAppDefine.timeLimitMin -= self.deductionTime
            #print("nextBtn")
            #print(mAppDefine.timeLimitMin)
            parent.SetStartTime(mAppDefine.timeLimitMin*mAppDefine.MIN_TO_SEC)
            mAppDefine.timerFlag = True
            parent.start_timer()

            connect_handler = threading.Thread(target=self.sendStartSignalOffice,daemon=True)
            connect_handler.start()

            parent.SetGameView()
            parent.show_frame(mAppDefine.View.LOEGameView) 
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
    