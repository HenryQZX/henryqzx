import random

import cv2
from remi import start, App
from remi.gui import *

if sys.version_info < (3, 5):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen
import numpy as np

import base64


def base64_to_style_image(base64_image):
    return 'data:image/png;base64,' + base64_image


try:
    import socketio

    sio = socketio.Client()
    sio.connect('ws://0.0.0.0:8000')
    socket_connection = True
except:
    socket_connection = False

import time, signal, threading
import mmkv

mmkv.MMKV.initializeMMKV('/tmp/mmkv')
import android

droid = android.Android()
iport = random.randint(10000, 65534)
num_cam = 1
cache_frames = [None, None]


class OpencvVideoWidget(Image):

    def __init__(self, app_instance, **kwargs):
        super(OpencvVideoWidget, self).__init__(**kwargs)
        self.app_instance = app_instance

    def update(self):
        self.app_instance.execute_javascript(
            "\n            var url = '/%(id)s/get_image_data';\n            var xhr = new XMLHttpRequest();\n            xhr.open('GET', url, true);\n            xhr.responseType = 'blob'\n            xhr.onload = function(e){\n            var urlCreator = window.URL || window.webkitURL;\n            var imageUrl = urlCreator.createObjectURL(this.response);\n            document.getElementById('%(id)s').src = imageUrl;\n            }\n            xhr.send();\n            " % {
                'id': self.identifier})

    def idle(self):
        pass

    def ondata(self, filedata, filenames):
        pass

    def get_image_data(self, index=0):
        frame = cache_frames[index]
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                headers = {'Content-type': 'image/jpeg'}
                return [jpeg.tostring(), headers]
        return (None, None)


def close(signum, frame):
    print('You choose to stop me.')
    droid.usbCamClose()
    droid.realCamClose()
    droid.shutdown()
    if socket_connection:
        sio.emit('request_close_window', {'data': {'url': 'http://0.0.0.0:' + str(iport), 'title': sys.argv[0]}})
    kill(sys.argv[0])
    sys.exit()


def kill(pname):
    print("kill=%s" % pname)
    urlopen('http://127.0.0.1:9000/?name=kill~' + pname)


# deprecated
def quit(signum, frame):
    print('You choose to stop me.')
    kill(sys.argv[0])
    sys.exit()


def lfce(xxy):
    urlopen('http://127.0.0.1:8910/lfce?key=' + xxy)


def startx(xxy=''):
    try:
        signal.signal(signal.SIGINT, quit)
        signal.signal(signal.SIGTERM, quit)
        a = threading.Thread(target=lfce, args=(xxy,))
        a.setDaemon(True)
        a.start()
    except Exception as exc:
        print(exc)

    sleep(2000)


def initgui(loop, pid):
    try:
        signal.signal(signal.SIGINT, quit)
        signal.signal(signal.SIGTERM, quit)
        a = threading.Thread(target=loop, args=(pid,))
        a.setDaemon(True)
        a.start()
    except Exception as exc:
        print(exc)


class Aid_Dialog(App):
    def __init__(self, *args):
        super(Aid_Dialog, self).__init__(*args)

    def idle(self):
        # pass
        for i in range(num_cam):
            eval("self.aidcam%(i)s.update()" % {'i': i})
        self.lbl.set_text(cvs.getLbs())

    def main(self):
        return Aid_Dialog.construct_ui(self)

    @staticmethod
    def construct_ui(self):
        main_container = VBox(
            style={"width": "100%", "height": "100%", "position": "absolute", "top": "0px", "left": "0px",
                   "margin": "0px", "overflow": "auto"})
        for i in range(num_cam):
            exec("self.aidcam%(i)s = OpencvVideoWidget(self)" % {'i': i})
            exec("self.aidcam%(i)s.identifier = 'aidcam%(i)s'" % {'i': i})
            eval("main_container.append(self.aidcam%(i)s)" % {'i': i})
        self.lbl = Label('info:', width='360px', height='30px', style={'margin': '10px'})
        main_container.append(self.lbl)
        return main_container


def sleep(ntime=30):
    time.sleep(ntime / 1000.0)


def initcv(loop, myapp=Aid_Dialog):
    try:
        signal.signal(signal.SIGINT, close)
        signal.signal(signal.SIGTERM, close)
        a = threading.Thread(target=loop, args=(myapp,))
        a.setDaemon(True)
        a.start()
    except Exception as exc:
        print(exc)


def startcv(myapp=Aid_Dialog):
    print('app runs on port:', iport)
    s = start(myapp, update_interval=0.03, address='0.0.0.0', port=iport, start_browser=False, enable_file_cache=False)


class cv3:

    def __init__(self):
        self.haswin = False
        self.ui = 0
        self.lbs = ''
        self.frames_index = {}
        self.kvs = {}
        self.__version__ = "ver.2021.10.29"
        self.__cam__ = "camid 1：打开前置摄像头 0：打开后置摄像头 -1：一个usb摄像头 -2 ：全部打开两个USB摄像头 -3：打开两个摄像头中的一个 -4：打开两个摄像头的另一个-5：全部打开工业摄像头 -6：打开工业摄像头的一个 -7：打开工业摄像头的另一个 -8：打开网口摄像头"

    def setCustomUI(self, ui=1):
        self.ui = ui

    def read(self):
        ims = []
        # for kv in self.kvs.values():
        for k, v in self.kvs.items():
            index = v.getInt('trigger')
            # 判断index，如果没有变化，则表明是缓冲区的图没有更新
            if index == 0 or self.frames_index[k] == index:
                continue
            self.frames_index[k] = index
            bt = v.getBytes('jpegdata')
            v.set(True, 'needdata')
            nparr = np.frombuffer(bt, dtype=np.uint8)
            img = None
            if nparr.shape[0] != 0:
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            ims.append(img)

        if len(ims) == 0:
            return None
        elif len(ims) == 1:
            if ims[0] is None:
                return None
            return ims[0]
        elif len(ims) == 2:
            if ims[0] is None and ims[1] is None:
                return None
            elif ims[0] is not None and ims[1] is None:
                return ims[0]
            elif ims[0] is None and ims[1] is not None:
                return ims[1]
            else:
                return ims
        else:
            # 超过2个摄像头，理论上不会走这个分支
            print("the camera num is over")
            return ims

    def imshow(self, im, ntime=0, myapp=Aid_Dialog):
        global cache_frames
        for kv in self.kvs.values():
            kv.set(True, 'needdata')
        if self.haswin == False:
            if self.ui == 0:
                initcv(startcv, myapp)
            droid.realCamOpen(9, sys.argv[0], iport, 0, 0, 0, "", 1)
            self.haswin = True
        if type(im) is list:
            for index, item in enumerate(im):
                bf = True
                if item is None:
                    bf = False
                if bf:
                    cache_frames[index] = item
        else:
            bf = True
            if im is None:
                bf = False
            if bf:
                cache_frames[0] = im

    def VideoCapture(self, camid=1, show_win=True, cam_w=640, cam_h=480, quality=50, exposureTime=40000, gain=1,
                     trigerModel=1, trigerActivation=0, myapp=Aid_Dialog):
        # rpc apply permission
        if camid >= 0 and camid != 9:
            ret = droid.requestCameraPermission()
            if ret.result is False:
                print('failed to request permission.')
                return
        global num_cam
        if camid == -2 or camid == -5:
            num_cam = 2
        for i in range(num_cam):
            self.kvs['kv' + str(i)] = mmkv.MMKV('aid_cam_' + str(i), mmkv.MMKVMode.MultiProcess)
            self.frames_index['kv' + str(i)] = 0

        for kv in self.kvs.values():
            kv.set(True, 'needdata')
        if self.ui == 0:
            initcv(startcv, myapp)
        if camid < 0:
            droid.UsbCamOpen(camid, sys.argv[0], iport, cam_w, cam_h, quality, 0, exposureTime, gain, trigerModel,
                             trigerActivation)
        else:
            droid.realCamOpen(camid, sys.argv[0], iport, cam_w, cam_h, quality)
        self.haswin = True
        if camid < 9:
            print('open the cam:' + str(camid) + ' ...')
        if socket_connection and show_win:
            sio.emit('request_open_window', {
                'data': {'url': 'http://0.0.0.0:' + str(iport), 'title': sys.argv[0], 'icon': '', 'camid': camid}})
        return self

    def openwin(self):
        return self.VideoCapture(9)

    def setLbs(self, lbs):
        self.lbs = lbs

    def getLbs(self):
        return self.lbs

    # cv2 commands
    def imread(self, *args):
        return cv2.imread(*args)

    def waitKey(ntime):
        keycode = cv2.waitKey(ntime)
        return keycode

    def rectangle(self, *args):
        cv2.rectangle(*args)

    def line(self, *args):
        cv2.line(*args)

    def circle(self, *args):
        cv2.circle(*args)

    def putText(self, *args):
        cv2.putText(*args)

    def GaussianBlur(self, *args):
        return cv2.GaussianBlur(*args)

    def flip(self, *args):
        return cv2.flip(*args)

    def resize(self, *args):
        return cv2.resize(*args)

    # base64 commands
    def im_read(self, file_name):
        with open(file_name, "rb") as f:
            bs64_str = base64.b64encode(f.read())
            if not isinstance(bs64_str, str):
                # Python 3, decode from bytes to string
                bs64_str = bs64_str.decode()
            return base64_to_style_image(bs64_str)


cvs = cv3()
