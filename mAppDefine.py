from enum import Enum

# Connection
officeServerIP = '192.168.219.226'
officeServerPort = 1919

portNumber = 1919

themeType = 'LOE'
themeTypeString_LOE = 'LOE'
codeType_START = 'START'
codeType_HELP = 'HELP'
codeType_END = 'END'

codeTypeString_START = "START"
codeTypeString_END = "END"
codeTypeString_SUBEND = "SUBEND"
codeTypeString_HINT = "HINT"
codeTypeString_HELP = "HELP"
codeTypeString_DEFAULT = "DEFAULT"
codeTypeString_MAGNETIC = "MAG"

#device
email = "araka0279@naver.com"
password = "znznfna19"

light_top_01= "98:ba:5f:da:f8:23" # 6
light_mid_01= "98:03:8e:9c:c4:c8" # 174
light_bot_01= "98:03:8e:9c:c6:be" # 103

remote_magnetic_01 = "24:d7:eb:ef:ad:63"

# DB
dataPath = "LOE2.db"

## protocol data
PD_INIT = "LIN"
PD_TEST = 'LTT'
PD_START = 'L00'
PD_LOE01 = ':01'


cardFileNameIndex = 2
cardAnswerTextIndex = 3
cardGradeIndex = 4
cardGuideTextIndex = 5
cardHintTextIndex = 6
cardAnswerTypeIndex = 7

itemNameIndex = 1
itemFileNameIndex = 2
itemTextIndex = 3
itemTargetIndex = 4
itemTypeIndex = 5
itemValueIndex = 6

# SpuIntroView
nextButton_rel_x = 0.8
nextButton_rel_y = 0.6

layerInputButton_rel_x = 0.45
layerInputButton_rel_y = 0.5

## SpuGameView

# guideText
guideTextWidth = 650
guideTextHeight = 210
guideTextFrameX = 50
guideTextFrameY = 50
guideTextDefault = "문제를 물리치기 어려우면 가이드 토큰을 사용해보세요~!"
guideTextX = 5
guideTextY = 5
guideTextBright = 0.5

# cardFrame
frameStartX = 150
frameStartY = 315
frameWidth = 400
frameHeight = 470

# color
timerColor = "#7A5423"
nextButtonColor = "#C86940"
helpButtonColor = "#C86940"
endButtonColor = "#C86940"
inputButtonColor = "#877129"

# popup

endingPopupText1 = '층 까지 올랐지만 이 위에도 더 층이 있는 것 같습니다.'
endingPopupText2 = '그렇지만 오늘은 더 오를 수 없습니다. 다음에는.. 꼭..!'
commonPopupGeometry = f"700x200+800+575"
resetPopupGeometry = f"1400x800+200+150"
endingPopupGeometry = f"1200x600+200+150"
itemPopupGuiIndex1 = 0
itemPopupGuiIndex2 = 1
itemPopupGuiIndex3 = 2

# global
root_path = 'C:\\LOE\\'
common_font = '경기천년바탕OTF Regular'
plusLayer = 36
intro_png = 'IntroBg.png'
gameView_png = 'LOEBg.png'
LOELaserPortFilePath = 'LOELaserPort.txt'

helpCall = '직원호출'
endCall = '테마종료'

startCode = 'START'
testCode = 'TEST'
exitCode = 'EXIT'

timerFlag = False

timeLimitMin = 99 # min
MIN_TO_SEC = 60 # sec
ONE_MIL_SEC = 1000 # msec
HALF_MIL_SEC = 200 # msec
MIL_SEC_100 = 100 # msec
MIL_SEC_10 = 10 # msec
ONE_SEC = 1 # sec

class ItemState(Enum):
    NotUsed = 0
    Using = 1
    Used = 2

class CardState(Enum):
    NotUsed = 0
    Using = 1
    Over = 2

class CardGrade(Enum):
    Undefined = 0
    Easy = 1
    Normal = 2
    Hard = 3
    Curse = 4

class AnswerType(Enum):
    Special = 0
    Single = 1
    Multi = 2

class View(Enum) :
    LOEIntroView = 0
    LOEGameView = 1

class AppDefine():
    _instance = None

    # singleton global

    def __new__(cls_, *args, **kwargs):
        if cls_._instance is None:
            cls_._instance = super().__new__(cls_,*args,**kwargs)
        else:
            return cls_._instance
        
    def __init__(self):
        cls_ = type(self)
        if not hasattr(cls_, '_init'):
            cls_._init = True
        