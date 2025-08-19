import tkinter as tk

import mAppDefine
import mTimer

import pygame
import sqlite3
import socket
import threading
import json
import random
import sys
import textwrap

from datetime import datetime
from PIL import Image, ImageTk, ImageEnhance

class LOEGameView(tk.Frame):

    remainTimer = None
    endFlag = False
    itemPopupState = False

    quizImageArray = []
    quizAnswerArray = []
    quizHintArray = []
    quizGuideArray = []

    quizCount = 0
    hintCount = 0

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)

        self.upperView = parent

        self.Init_BGM()
        self.Init_QUIZ()

        self.exitCount = 0
        self.endFlag = False
        self.currentQuizIndex = 0

        image_path = mAppDefine.root_path + mAppDefine.gameView_png    
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        #self.canvas.pack(fill="both", expand=True)
        self.canvas.place(x=0,y=0)
        self.prevImage = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)        

        quizImagePath = mAppDefine.root_path + self.quizImageArray[self.currentQuizIndex]
        self.quizImage = Image.open(quizImagePath)
        self.resizedQuizImage = self.quizImage.resize((1920, 1080), Image.LANCZOS)
        self.quizPhoto = ImageTk.PhotoImage(self.resizedQuizImage)
        self.quizCanvas = tk.Canvas(self, width=self.resizedQuizImage.width, height=self.resizedQuizImage.height, highlightthickness=0, bd=0)
        self.quizCanvas.place(x=0,y=0)
        self.quizCanvas.photoRef = self.quizPhoto
        self.prevQuizImage = self.quizCanvas.create_image(0, 0, anchor=tk.NW, image=self.quizPhoto)

        ## timer
        self.remainTimer = mTimer.Timer(self)
        self.remainTimer.place(x=25,y=980)

        ## helpLifeFrame
        self.helpLifeFrame = tk.Frame(self)
        self.helpLifeFrame.place(x=200,y=980)

        #self.helpButton = tk.Button(self.helpLifeFrame, text=mAppDefine.helpCall, font = (mAppDefine.common_font,20), width = 10, height = 2, command=lambda: self.open_help_popup(), fg="white",bg=mAppDefine.helpButtonColor)
        #self.helpButton.pack(side=tk.LEFT)

        self.hintCountButton = tk.Button(self.helpLifeFrame,text=str(self.hintCount), font=(mAppDefine.common_font,20), width=5, height=2, command=lambda:self.hint_button_popup(), fg="white", bg=mAppDefine.helpButtonColor, activebackground="white", activeforeground="red")
        self.hintCountButton.pack(side=tk.LEFT)
        
    def hint_button_popup(self):
        return

    def OnUpdate(self):
        print('gameView onUdpate')

    def Init_BGM(self):
        pygame.init()
        pygame.mixer.init()

    def Init_bg(self):
        image_path = mAppDefine.root_path + mAppDefine.gameView_png
        self.newImage = Image.open(image_path)
        self.newPhoto = ImageTk.PhotoImage(self.newImage)
        self.canvas.delete(self.prevImage)
        self.canvas.create_rectangle(0, 0, 100, 100, fill='red')
        self.prevImage = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.newPhoto)

    def Init_QUIZ(self):
        self.Sqlite_Quiz()

        for i in range(0,self.quizCount):
            self.quizImageArray.append(self.quizDataRaws[i][1])
            self.quizAnswerArray.append(self.quizDataRaws[i][2])
            self.quizHintArray.append(self.quizDataRaws[i][3])      
            self.quizGuideArray.append(self.quizDataRaws[i][4])

        print(self.quizImageArray)        
     
    def SetHint(self,_hintText):
        self.hintCount += 1
        self.hintCountButton.config(text=str(self.hintCount))
        
    def stop_game(self):
        self.start_ending()

    def start_ending(self):
        if(self.endFlag == True):
            return

    def open_help_popup(self):
        popup = tk.Toplevel(self)
        popup.title("직원호출")
        popup.geometry(mAppDefine.commonPopupGeometry)

        popup.overrideredirect(True)

        def onClickHelpBtn():
            connect_handler = threading.Thread(target=self.sendHelpSignalOffice,daemon=True)
            connect_handler.start()
            popup.destroy()   
            
        label = tk.Label(popup, text="직원을 호출하시겠습니까?",font = (mAppDefine.common_font,30))
        label.pack()
        
        button1 = tk.Button(popup, text="네",font = (mAppDefine.common_font,20), command=onClickHelpBtn)
        button1.pack(pady=10)

        button2 = tk.Button(popup, text="닫기",font = (mAppDefine.common_font,20), command=popup.destroy)
        button2.pack()

    def sendHelpSignalOffice(self):
        print("sendHelpSignalOffice")
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((mAppDefine.officeServerIP, mAppDefine.officeServerPort))  # 서버의 호스트와 포트에 연결

        # 서버로 데이터 전송
        data_to_send = {
            "themeType" : mAppDefine.themeType,
            "codeType" : mAppDefine.codeType_HELP,
            "msg" : mAppDefine.codeTypeString_HELP
        }
        json_data = json.dumps(data_to_send)
        client_socket.sendall(json_data.encode('utf-8'))
        client_socket.close()

    def sendEndSignalOffice(self): 
        print("sendEndSignalOffice")        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((mAppDefine.officeServerIP, mAppDefine.officeServerPort))  # 서버의 호스트와 포트에 연결 #

        timeStr = self.remainTimer.GetCurrnetTimeLabel()
        # 서버로 데이터 전송
        data_to_send = {
            "themeType" : mAppDefine.themeType,
            "codeType" : mAppDefine.codeType_END,
            "msg" : timeStr
        }
        json_data = json.dumps(data_to_send)
        client_socket.sendall(json_data.encode('utf-8'))
        client_socket.close()  

    def Sqlite_Quiz(self):
        cardConn = sqlite3.connect(mAppDefine.root_path + mAppDefine.dataPath)
        cardCursor = cardConn.cursor()
        try:
            # 테이블이 존재하는지 확인
            cardCursor.execute('''
                SELECT name FROM sqlite_master WHERE type='table' AND name='LOE_QUIZ'
            ''')
            table_exists = cardCursor.fetchone()

            if table_exists:
                # 테이블이 존재하는 경우 데이터 읽기
                query = 'SELECT max(QUIZ_INDEX) FROM LOE_QUIZ'
                cardCursor.execute(query)

                count = cardCursor.fetchall()
                self.quizCount = count[0][0]
                self.quizCount += 1
                print("cardCount : ",self.quizCount)

                query2 = 'SELECT * FROM LOE_QUIZ'
                cardCursor.execute(query2)

                # 결과 가져오기
                self.quizDataRaws = cardCursor.fetchall()     

                # 결과 출력
                #for row in self.dataRaws:
                    #print(row)
            else:
                print("테이블이 존재하지 않습니다.")
        except sqlite3.Error as e:
            print("SQLite 에러:", e)

        finally:
            # 연결 종료
           cardConn.close()


    def updateFrame(self):
        print("")
    
    def SetStartTime(self,_time):
        self.remainTimer.SetStartTime(_time)

    def start_timer(self):
        self.remainTimer.start_timer()