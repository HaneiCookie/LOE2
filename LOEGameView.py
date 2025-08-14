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

        image_path = mAppDefine.root_path + mAppDefine.gameView_png    
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        #self.canvas.pack(fill="both", expand=True)
        self.canvas.place(x=0,y=0)
        self.prevImage = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        ## timer
        self.remainTimer = mTimer.Timer(self)
        self.remainTimer.pack(pady=10)

        # guideText
        self.guideTextFrame = tk.Frame(self, width=mAppDefine.guideTextWidth, height=mAppDefine.guideTextHeight, bg="red")
        self.guideTextFrame.place(x=mAppDefine.guideTextFrameX,y=mAppDefine.guideTextFrameY)

        cropImage = self.image.crop((mAppDefine.guideTextFrameX,mAppDefine.guideTextFrameY,mAppDefine.guideTextFrameX+mAppDefine.guideTextWidth,mAppDefine.guideTextFrameY+mAppDefine.guideTextHeight))
        enhancer = ImageEnhance.Brightness(cropImage)
        self.cropped_image = enhancer.enhance(mAppDefine.guideTextBright)
        self.guideTextPhoto = ImageTk.PhotoImage(self.cropped_image)
        self.guideTextCanvas = tk.Canvas(self.guideTextFrame, width=mAppDefine.guideTextWidth, height=mAppDefine.guideTextHeight, borderwidth=0, highlightthickness=0)
        self.guideTextCanvas.create_image(0,0,anchor=tk.NW, image=self.guideTextPhoto)
        
        wrapped_text = textwrap.fill(mAppDefine.guideTextDefault, width=20)
        self.current_guide_text = self.guideTextCanvas.create_text(mAppDefine.guideTextX,mAppDefine.guideTextY, anchor=tk.NW, text=wrapped_text, font=(mAppDefine.common_font,25), fill="white")
        self.guideTextCanvas.place(x=0,y=0)

        ## helpLifeFrame
        self.helpLifeFrame = tk.Frame(self)
        self.helpLifeFrame.pack(pady=10)

        self.helpButton = tk.Button(self.helpLifeFrame, text=mAppDefine.helpCall, font = (mAppDefine.common_font,20), width = 10, height = 2, command=lambda: self.open_help_popup(), fg="white",bg=mAppDefine.helpButtonColor)
        self.helpButton.pack(side=tk.LEFT)

        self.hintCountButton = tk.Button(self.helpLifeFrame,text=str(self.hintCount), font=(mAppDefine.common_font,20), width=5, height=2, command=lambda:self.open_guide_token_popup(), fg="white", bg=mAppDefine.helpButtonColor, activebackground="white", activeforeground="red")
        self.hintCountButton.pack(side=tk.LEFT)
        
        self.exitCount = 0

        self.Init_BGM()
        self.Init_QUIZ()

        ## quizFrame
        #self.quizFrame = tk.Frame(self)
        #self.quizFrame.pack(pady=10)

        self.currentQuizIndex = 0

        quizImagePath = mAppDefine.root_path + self.quizImageArray[self.currentQuizIndex]
        self.quizImage = Image.open(quizImagePath)
        self.quizPhoto = ImageTk.PhotoImage(self.quizImage)
        self.quizCanvas = tk.Canvas(self, width=self.quizImage.width, height=self.quizImage.height, highlightthickness=0, bd=0)
        self.quizCanvas.pack()
        self.quizCanvas.photoRef = self.quizPhoto
        self.prevQuizImage = self.quizCanvas.create_image(0, 0, anchor=tk.NW, image=self.quizPhoto)

        self.endFlag = False

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