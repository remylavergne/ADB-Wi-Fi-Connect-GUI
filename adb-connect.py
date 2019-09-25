#!/usr/bin/env python3

import subprocess
import sys
import time

from PySide2.QtWidgets import (QLineEdit, QPushButton, QApplication, QDialog, QLabel, QGridLayout)


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("ADB Wi-Fi Connect 0.2")
        # Create widgets
        self.edit = QLineEdit("192.168.236.197")
        self.edit2 = QLineEdit("5555")
        self.button = QPushButton("Connect device")
        self.button2 = QPushButton("Disconnect device")
        self.label = QLabel("Output:")
        self.label2 = QLabel("")
        # Create layout and add widgets
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel('Device IP'), 0, 0)
        grid_layout.addWidget(self.edit, 1, 0, 1, 1)
        grid_layout.addWidget(QLabel('Port'), 0, 1, 1, 1)
        grid_layout.addWidget(self.edit2, 1, 1)
        # Buttons
        grid_layout.addWidget(self.button, 2, 0)
        grid_layout.addWidget(self.button2, 2, 1)
        # Output // addWidget(*Widget, row, column, rowspan, colspan)
        grid_layout.addWidget(self.label, 3, 0)
        grid_layout.addWidget(self.label2, 4, 0, 1, 2)

        # Set dialog layout
        self.setLayout(grid_layout)
        # Add button signal to greetings slot
        self.button.clicked.connect(self.adb_connect)
        self.button2.clicked.connect(self.disconnect)

        self.attempts = 0
        self.usb_plug_asked = False

    def adb_connect(self):
        self.label2.setText('')
        time.sleep(1)
        try:
            my_out = subprocess.Popen(f"adb connect {self.edit.text()}:{self.edit2.text()}",
                                      shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
            stdout, stderr = my_out.communicate()
            # Keep outputs
            output = str(stdout)
            # UNUSED output_error = str(stdout)
            # Process outputs
            self.process_outputs_messages(output)

        except subprocess.CalledProcessError as err:
            self.label2.setText('General fatal error. Please restart program.')

    def process_outputs_messages(self, output):
        if 'already' in output:
            self.label2.setText('Already connected...')
            return
        if 'connected' in output:
            if self.usb_plug_asked:
                self.label2.setText('Connected ! You can unplug the USB cable.')
                self.usb_plug_asked = False
            else:
                self.label2.setText('Connected !')
            return
        if 'protocol fault' in output:
            self.label2.setText('Check if device is turned on, please. And retry.')
        if 'failed to connect' in output:
            print(f'\tFailed to connected {self.edit.text()}')
            self.kill_adb()
            self.set_tcpip()

    @staticmethod
    def kill_adb():
        # Kill ADB server
        subprocess.Popen(f"adb kill-server",
                         shell=True)
        time.sleep(1)

    def set_tcpip(self):

        self.attempts += 1

        my_out = subprocess.Popen(f"adb tcpip {self.edit2.text()}",
                                  shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        stdout, stderr = my_out.communicate()

        if self.attempts > 2:
            self.label2.setText('Plug your phone to your computer via USB, please.\nAnd retry.')
            self.attempts = 0
            self.usb_plug_asked = True
            return

        if 'error: no devices/emulators found' in str(stdout):
            print('Attemp to reconnect device to adb')
            self.adb_connect()
        else:
            print('Force tcpip reset')
            self.set_tcpip()

    def disconnect(self):
        subprocess.Popen(f"adb disconnect {self.edit.text()}",
                         shell=True)
        self.kill_adb()
        self.label2.setText(f'Device {self.edit.text()}:{self.edit2.text()} has been disconnected.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    sys.exit(app.exec_())
