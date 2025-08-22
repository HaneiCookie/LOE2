import tkinter as tk
import mAppDefine

from LOEIntroView import LOEIntroView
from LOEGameView import LOEGameView


class LOEView(tk.Tk):

    introView = None
    gameView = None

    frames = {}

    def __init__(self):
        tk.Tk.__init__(self)

        self.geometry("1920x1080")
        self.attributes("-fullscreen",False)
        self.bind("<Escape>", self.quitFullScreen)
      
        self.Init_GUI()
        self.show_frame(mAppDefine.View.LOEIntroView)

        #self.OnUpdate()

    def OnUpdate(self):
        self.gameView.OnUpdate()

        self.after(mAppDefine.ONE_MIL_SEC,self.OnUpdate)

    def Init_GUI(self) :
        self.frames = {}
        self.introView = LOEIntroView(self)
        self.frames[mAppDefine.View.LOEIntroView] = self.introView
        self.introView.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.gameView = LOEGameView(self)
        self.frames[mAppDefine.View.LOEGameView] = self.gameView
        self.gameView.place(x=0, y=0, relwidth=1, relheight=1)

        self.SetViewConnection()

    def SetViewConnection(self):
        self.gameView.SetViewConnection()

    def GetIntroView(self):
        return self.frames[mAppDefine.View.LOEIntroView]
        print("GetIntroView")
    
    def SetGameView(self):
        self.gameView.Init_bg()

    def SetBGM(self):
        self.gameView.Init_BGM()

    def SetStartTime(self,_time):
        #print("parnet SetStartTime")
        #print(_time)
        self.gameView.SetStartTime(_time)

    def start_timer(self):
        #print("parnet start_timer")
        self.gameView.start_timer()    

    def show_frame(self, view):
        # 선택한 화면을 보여줍니다.
        frame_to_show = self.frames[view]
        frame_to_show.updateFrame()
        frame_to_show.tkraise()

    def quitFullScreen(self, event):
        self.attributes("-fullscreen", False)