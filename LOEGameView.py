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
    quizHintImageArray = []
    quizGuideArray = []
    movingImageArray = []
    doubleLeftImageArray = []
    doubleRightImageArray = []

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

        self.hintCountButton = tk.Button(self.helpLifeFrame,text=str(self.hintCount), font=(mAppDefine.common_font,20), width=5, height=2, command=lambda:self.hint_button_popup(), fg="white", bg=mAppDefine.helpButtonColor, activebackground="white", activeforeground="red")
        self.hintCountButton.pack(side=tk.LEFT)

        self.entry = tk.Entry(self,width = 10, font = (mAppDefine.common_font,53))
        self.entry.bind("<Return>", self.onEnterCardInput)
        self.entry.place(x=800,y=980)

        self.left_split_end_check = False
        self.right_split_end_check = False

    def onEnterCardInput(self,event):
        inputText = self.entry.get().upper()

        print(self.currentQuizIndex)
        print(inputText)

        if(self.currentQuizIndex == 34):
            if(inputText == "JAYA"):
                self.show_left_quiz(1)
            elif(inputText == "RAKAN"):
                self.show_right_quiz(1)
            elif(inputText == "이쉬탈"):
                self.show_left_quiz(2)
            elif(inputText == "블롱코"):
                self.show_right_quiz(2)
            elif(inputText == "0122"):
                self.show_left_quiz(3)
                self.left_split_end_check = True
            elif(inputText == "너무보고시퍼"):
                self.show_right_quiz(3)
                self.right_split_end_check = True

        if(self.left_split_end_check == True and self.right_split_end_check == True):
            self.currentQuizIndex = 37
            self.left_split_end_check = False
            self.right_split_end_check = False

        #skip test
        if(inputText == "TT"):
            self.currentQuizIndex = 34
            self.show_next_quiz()   

        if(inputText == "직원호출"):
            self.sendHelpSignalOffice()
        elif(inputText == "힌트다힌트"):
            self.show_hint_content()
        elif(self.check_answer(inputText) == True):    
            self.currentQuizIndex += 1        
            self.show_next_quiz()
        else:
            print("no answer")

        self.entry.delete(0,tk.END)

    def show_hint_content(self):
        newImagePath = mAppDefine.root_path + self.quizHintImageArray[self.currentQuizIndex]
        newImage = Image.open(newImagePath).resize((1920, 1080), Image.LANCZOS)
        newPhoto = ImageTk.PhotoImage(newImage)
        self.quizCanvas.itemconfig(self.prevQuizImage, image=newPhoto)
        self.quizCanvas.photoRef = newPhoto

    def check_answer(self,_inputText):
        if(self.quizAnswerArray[self.currentQuizIndex].upper() == _inputText):
            return True
        else:
            return False        
        
    def show_next_quiz(self):       
        newImagePath = mAppDefine.root_path + self.quizImageArray[self.currentQuizIndex]
        newImage = Image.open(newImagePath).resize((1920, 1080), Image.LANCZOS)
        newPhoto = ImageTk.PhotoImage(newImage)
        self.quizCanvas.itemconfig(self.prevQuizImage, image=newPhoto)
        self.quizCanvas.photoRef = newPhoto

        if(self.currentQuizIndex >= 25 and self.currentQuizIndex <= 30):
            self.show_moving_quiz()
        elif(self.currentQuizIndex == 34):
            self.show_left_quiz(self.currentQuizIndex-34)
            self.show_right_quiz(self.currentQuizIndex-34)
        elif(self.currentQuizIndex >= 37 and self.currentQuizIndex <= 41):
            self.show_left_quiz(self.currentQuizIndex-34)
            self.show_right_quiz(self.currentQuizIndex-34)
    
    def move_image(self):
        self.movingImage_x -= 2
        self.quizCanvas.coords(self.movingImage,self.movingImage_x,self.movingImage_y)
        if(self.movingImage_x <= -2880):
            self.movingImage_x = -2880
            self.move_time_count += 1
            print(self.movingImage_x)
            print(self.move_time_count)
            if(self.move_time_count >= mAppDefine.ONE_SEC*5):
                self.move_time_count = 0
                self.movingImage_x = 0

        self.after(mAppDefine.MIL_SEC_10,lambda:self.move_image()) 

    def show_moving_quiz(self):
        newImagePath = mAppDefine.root_path + self.movingImageArray[self.currentQuizIndex-25]
        newImage = Image.open(newImagePath).resize((5040, 1080), Image.LANCZOS)
        newPhoto = ImageTk.PhotoImage(newImage)
        self.movingImage_x = 0
        self.movingImage_y = 0
        self.movingImage = self.quizCanvas.create_image(self.movingImage_x,self.movingImage_y,anchor=tk.NW,image=newPhoto)
        #self.quizCanvas.itemconfig(self.prevQuizImage, image=newPhoto)
        self.quizCanvas.photoRef = newPhoto

        self.move_time_count = 0
        self.move_image()
    
    def show_left_quiz(self,index):
        newImagePath = mAppDefine.root_path + self.doubleLeftImageArray[index]
        newImage = Image.open(newImagePath).resize((960, 1080), Image.LANCZOS)
        newPhoto = ImageTk.PhotoImage(newImage)
        self.leftImage = self.quizCanvas.create_image(0,0,anchor=tk.NW,image=newPhoto)
        self.quizCanvas.leftRef = newPhoto

    def show_right_quiz(self,index):
        newImagePath = mAppDefine.root_path + self.doubleRightImageArray[index]
        newImage = Image.open(newImagePath).resize((960, 1080), Image.LANCZOS)
        newPhoto = ImageTk.PhotoImage(newImage)
        self.leftImage = self.quizCanvas.create_image(960,0,anchor=tk.NW,image=newPhoto)
        self.quizCanvas.rightRef = newPhoto
        
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
            self.quizHintImageArray.append(self.quizDataRaws[i][3])      
            self.quizGuideArray.append(self.quizDataRaws[i][4])

        for j in range(0,7):
            self.movingImageArray.append("LOE_MID_MOIVE_IMAGE.0" + f"{j+1:02}" + ".png")

        for k in range(0,8):
            self.doubleLeftImageArray.append("LOE_Quiz_BOT.0" + f"{2*(k+1)-1:02}" + ".png")
            self.doubleRightImageArray.append("LOE_Quiz_BOT.0" + f"{2*(k+1):02}" + ".png")    
     
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

    def updateFrame(self):
        print("")
    
    def SetStartTime(self,_time):
        self.remainTimer.SetStartTime(_time)

    def start_timer(self):
        self.remainTimer.start_timer()