import tkinter as tk
import tkinter.ttk as ttk


import mAppDefine

class Timer(tk.Frame):

    startTime = 0
    remainTime = 0
    label_clock = None
    progress_bar = None #: ttk.Progressbar

    def __init__(self,parent):
        tk.Frame.__init__(self, parent)

        self.config(bg=mAppDefine.timerColor)

        self.gameView = parent

        self.startTime = mAppDefine.timeLimitMin*mAppDefine.MIN_TO_SEC # sec
        #print("mtimer")
        #print(mAppDefine.timeLimitMin)
        self.remainTime = self.startTime # sec
        self.label_clock = tk.Label(self, text = '{0:02d}'.format(self.startTime//(mAppDefine.MIN_TO_SEC)) + ":" + '{0:02d}'.format(self.startTime%(mAppDefine.MIN_TO_SEC)), font = (mAppDefine.common_font,50),fg="white",bg=mAppDefine.helpButtonColor)
        self.label_clock.pack()
        #self.progress_bar = ttk.Progressbar(self, orient = "horizontal", maximum=100, length = 500, mode = "determinate", variable=self.remainTime)
        #self.progress_bar.pack(pady=10)

    def update_timer(self):
        #print("timer update_timer")
        #print(self.remainTime)
        if(mAppDefine.timerFlag == True and self.remainTime > 0):
            self.remainTime -= mAppDefine.ONE_SEC
            self.label_clock.config(text = '{0:02d}'.format(self.remainTime//mAppDefine.MIN_TO_SEC) + ":" + '{0:02d}'.format(self.remainTime%mAppDefine.MIN_TO_SEC)) 
            #self.update_progressbar()
        self.label_clock.after(mAppDefine.ONE_MIL_SEC,self.update_timer)

        if(self.remainTime == 0):
            self.remainTime -= mAppDefine.ONE_SEC
            mAppDefine.timerFlag = False
            self.gameView.start_ending()

    def update_progressbar(self):
        progress_value = format((100-float((self.remainTime/self.startTime)*100)),".2f")
        #print(progress_value)
        self.progress_bar["value"] = progress_value
        #self.progress_bar.update()

    def SetStartTime(self,_time):
        self.startTime = _time
        self.remainTime = self.startTime
        #print("timer setstarttime")
        #print(self.remainTime)

    def start_timer(self):
        #print("timer start_timer")
        #print(self.remainTime)
        self.update_timer()

    def GetCurrentTime(self):
        return self.remainTime # sec
    
    def GetCurrnetTimeLabel(self):
        return self.label_clock.cget("text")