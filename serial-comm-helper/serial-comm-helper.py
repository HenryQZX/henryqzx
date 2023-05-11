from remi import App, start
import remi.gui as gui
import json
import time

use_android = True # 调试UI 0
droid = None
BaudRates = ['2400', '4800', '9600', '19200', '57600', '115200']

if use_android:
    import android

    droid = android.Android()


class SerialCommHelper(App):

    def __init__(self, *args, **kwargs):
        self.num_cam = kwargs.get('num_cam', 0)
        self.devices = []
        self.established = False
        super(SerialCommHelper, self).__init__(*args)

    def idle(self):
        # 10s刷新一次 device_list
        if self._is_refresh_time(now_time_second=time.localtime().tm_sec, interval_time=10) is True:
            try:
                self._refresh_dropDown(self.device_dropDown)
            except:
                pass
        self.accept_message()

    def main(self):
        return self.construct_ui()

    def construct_ui(self):
        # 主界面
        self.main_container = gui.Container(
            style={'width': '1024px', 'height': '768px', 'font-size': '24px',
                   'justify-content': 'flex-start', 'background': '#F4F5F5'})

        self.horizontalContainer = gui.Container(width='100%', height='100%',
                                                 layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
                                                 margin='0px', style={'display': 'block', 'overflow': 'auto',
                                                                      'background': '#F4F5F5'})
        self.choose_ui()
        self.main_container.append(self.horizontalContainer)
        return self.main_container

    def choose_ui(self):
        self.horizontalContainer.empty()
        subContainerLeft = gui.Container(width='50%',
                                         style={'display': 'block', 'overflow': 'auto', 'text-align': 'center',
                                                'background': '#F4F5F5'})
        # device label
        device_label = gui.Label('串口链接', style={'text-align': 'left', 'margin-left': '30px', 'margin-top': '20px',
                                                'width': '96px',
                                                'font-size': '14px',
                                                'font-weight': '500',
                                                'line-height': '22px',
                                                'color': '#3D3F42',
                                                'opacity': '1',
                                                })
        # device 下拉选择框
        self.device_dropDown = self._get_dropDown()
        device_label_tip = gui.Label('选择你需要的串口进行链接。',
                                     style={'text-align': 'left', 'margin-top': '20px', 'margin-left': '30px',
                                            'width': '200px',
                                            'font-size': '12px',
                                            'font-weight': '400',
                                            'line-height': '20px',
                                            'color': '#6D6D6D',
                                            'opacity': '1', })

        # button
        self.connect_button = gui.Button('连接', style={'margin-left': '30px', 'margin-top': '100px', 'width': '290px',
                                                      'height': '40px',
                                                      'background': '#3478F6',
                                                      'opacity': '1',
                                                      'border-radius': '10px'})
        self.connect_button.add_class("btn btn-primary")
        self.connect_button.onclick.do(self.connect_device)

        subContainerLeft.append([device_label, self.device_dropDown, device_label_tip, self.connect_button])

        subContainerRight = gui.Container(
            style={'width': '50%', 'display': 'block', 'overflow': 'auto', 'text-align': 'center',
                   'background': '#F4F5F5'})
        # 波特率 label && 下拉选择框
        baud_label = gui.Label('波特率', style={'text-align': 'left', 'margin-top': '20px',
                                             'width': '96px',
                                             'font-size': '14px',
                                             'font-family': 'Source Han Sans CN',
                                             'font-weight': '500',
                                             'line-height': '22px',
                                             'color': '#3D3F42',
                                             'opacity': '1',
                                             })
        self.baud_dropDown = self._get_dropDown_baud()
        baud_label_tip = gui.Label('选择你需要的波特率。', style={'text-align': 'left', 'margin-top': '20px',
                                                        'width': '200px',
                                                        'font-size': '12px',
                                                        'font-weight': '400',
                                                        'line-height': '20px',
                                                        'color': '#6D6D6D',
                                                        'opacity': '1', })
        subContainerRight.append([baud_label, self.baud_dropDown, baud_label_tip])

        self.horizontalContainer.append([subContainerLeft, subContainerRight])

    def jump_ui(self):
        self.horizontalContainer.empty()
        self.message_container = gui.Container(width='100%', height='85%',
                                               layout_orientation=gui.Container.LAYOUT_VERTICAL,
                                               style={'display': 'block', 'overflow': 'auto',
                                                      'text-align': 'left',
                                                      'background': '#F4F5F5', 'overflow-x': 'hidden'})
        containBottom = gui.Container(width='100%', height='15%',
                                      style={'display': 'block', 'overflow': 'hidden', 'text-align': 'left',
                                             'background': '#F4F5F5'})
        self.message_input = gui.TextInput(width='933px', height='100px',
                                           style={'margin-left': '30px', 'border-radius': '10px', 'opacity': '1',
                                                  'background': '#FFFFFF'})

        self.send_msg_div_style = {
            'background': '#3478F6', 'width': '200px',
            'border-top': '20px', 'border-radius': '10px', 'text-align': 'left', 'border-left': '20px',
            'margin-left': '30px'
        }
        self.accept_msg_div_style = {
            'background': '#FFFFFF',
            'width': '200px',
            'border-top': '20px', 'border-radius': '10px', 'text-align': 'left', 'border-right': '20px',
            'margin-left': '30px'
        }
        self.msg_label_style = {
            'word-wrap': 'break-word',
            'margin-left': '15px',
            'width': '170px',
            'margin-right': '15px',
        }
        self.send_button = gui.Button('发送', style={'margin-left': '80%', 'margin-top': '-10%', 'width': '120px',
                                                   'height': '40px',
                                                   'background': '#3478F6',
                                                   'opacity': '1',
                                                   'border-radius': '10px'})
        self.send_button.onclick.do(self.send_message)
        self.retrun_button = gui.Button('返回', style={'margin-left': '66%', 'margin-top': '-16%', 'width': '120px',
                                                     'height': '40px',
                                                     'background': '#17a2b8',
                                                     'opacity': '1',
                                                     'border-radius': '10px'})
        self.retrun_button.onclick.do(self.reset_connection)
        containBottom.append([self.message_input, self.send_button, self.retrun_button])

        self.horizontalContainer.append([self.message_container, containBottom])

    def send_message(self, widget):
        msg = self.message_input.get_value()
        if msg == '':
            return
        if use_android:
            droid.writeSerialData(msg.replace(' ', ''))
        # 左边添加空白div
        msg_div_right = gui.Container(width='100%',
                                      style={'background': '#F4F5F5', 'margin-top': '10px', 'margin-left': '550px'},
                                      layout_orientation=gui.Container.LAYOUT_VERTICAL)
        # 右边添加信息div
        msg_div_text = gui.Container(style=self.send_msg_div_style)
        msg_div_text.append(gui.Label(msg, style=self.msg_label_style))
        msg_div_right.append(
            [gui.Label(self._time_now(), style={'margin-left': '40px', 'font-size': '10px'}), msg_div_text])
        self.message_container.append(msg_div_right)

        self.message_input.set_value('')

    def accept_message(self):
        if self.established and use_android:
            message = droid.getReceiveData()[1]
            if message != "":
                message = str(message).upper()
                msg_div_left = gui.Container(width='100%', style={'background': '#F4F5F5', 'margin-top': '10px',
                                                                  'margin-left': '50px'},
                                             layout_orientation=gui.Container.LAYOUT_VERTICAL)
                # 左边添加信息div
                msg_div_text = gui.Container(style=self.accept_msg_div_style)
                msg_div_text.append(gui.Label(message, style=self.msg_label_style))
                msg_div_left.append(
                    [gui.Label(self._time_now(), style={'margin-left': '40px', 'font-size': '10px'}), msg_div_text])
                self.message_container.append(msg_div_left)

    def reset_connection(self, widget):
        if use_android:
            droid.disconnectSerialUsb()
        print('断开连接')
        self.established = False
        self.choose_ui()

    def connect_device(self, widget):
        select_device_id = self.device_dropDown.get_key()
        select_baud = self.baud_dropDown.get_value()
        if use_android:
            for device in self.devices:
                if device['deviceId'] == select_device_id:
                    connection = droid.connectSerialUsb(device['port'], device['deviceId'], select_baud)
                    print(connection)
                    connect_result = connection[1]
                    if connect_result == 'true':
                        self.established = True
                        print('连接成功')
        else:
            self.established = True
        if self.established:
            self.jump_ui()
        else:
            self.execute_javascript("""alert("connect failure")""")

    def update_device_list(self):
        if use_android:
            result = droid.startSearchSerialUsb()
            print(result)
            self.devices = json.loads(result[1])
        else:
            self.devices = [
                {"deviceId": 1002, "port": 0, "productId": 8963, "userDriverName": "Prolific", "venderId": 1659}]

    def _get_dropDown(self):
        drop_down = gui.DropDown(width='420px', height='40px')
        drop_down.style.update(
            {'font-size': 'large', 'background': '#FFFFFF', 'border': '1px solid #CFCFCF', 'opacity': '1',
             'border-radius': '10px', 'margin-left': '30px', 'margin-top': '20px'})
        drop_down.add_class("form-control dropdown")
        self._refresh_dropDown(drop_down)
        drop_down.style.update({'font-size': 'small'})

        return drop_down

    def _refresh_dropDown(self, drop_down):
        self.update_device_list()
        for device in self.devices:
            text = device['userDriverName'] + ' - deviceId:' + str(device['deviceId']) + ' - venderId:' + str(
                device['venderId'])
            item = gui.DropDownItem(text=text)
            drop_down.append(item, device['deviceId'])

    def _get_dropDown_baud(self):
        drop_down = gui.DropDown(width='420px', height='40px')
        drop_down.style.update(
            {'font-size': 'large', 'background': '#FFFFFF', 'border': '1px solid #CFCFCF', 'opacity': '1',
             'border-radius': '10px', 'margin-right': '30px', 'margin-top': '20px'})
        drop_down.add_class("form-control dropdown")
        [drop_down.append(gui.DropDownItem(text=element), element) for element in BaudRates]
        drop_down.style.update({'font-size': 'small'})
        return drop_down

    def _is_refresh_time(self, now_time_second, interval_time):
        if now_time_second % interval_time is 0:
            return True
        return False

    @staticmethod
    def _time_now():
        return time.strftime("%Y/%m/%d  %H:%M:%S", time.localtime())


if __name__ == "__main__":
    start(SerialCommHelper, debug=False, address='0.0.0.0', port=9901, update_interval=1, multiple_instance=False,
          start_browser=False, enable_file_cache=True)
