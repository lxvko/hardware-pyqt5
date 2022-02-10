import time

from PyQt5 import QtWidgets, uic, QtGui, QtTest
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from collect_data import organize_data

import wmi
import sys

# The value of the selected ones
# cpu               1     - CPU                - CPUTemp, CPULoad
# cpuclocks         2     - CPUClocks          - CPUClocks
# gpu               3     - GPU                - GPUTemp, GPULoad
# gpuclocks         4     - GPUClocks          - GPUClocks, GPUmemClocks
# gpumem            5     - GPUmem             - GPUmem, GPUmemFree
# ramuse            6     - RAMuse             - RAMuse
# rammem            7     - RAMmem             - RAMused, RAMfree
# uptime            8     - Uptime             - Uptime
# diskspace0123...  9     - DiskSpace.DiskName - DiskUsedSpace[i]
# diskusage0123...  10    - DiskUsage.DiskName - DiskRead[i], DiskWrite[i]

# Variables
count = 0
selected = []
disk_list = []
disk_selected = []
disk_selected_rw = []
unsorted_data = {}

# Launching the UI
app = QtWidgets.QApplication([])
ui = uic.loadUi('etc/hwmon.ui')
ui.setWindowIcon(QtGui.QIcon('etc/icon.jpg'))

# Configuring the Arduino Port
serial = QSerialPort()
serial.setBaudRate(115200)
portlist = []
ports = QSerialPortInfo().availablePorts()
for port in ports:
    portlist.append(port.portName())
ui.comlist.addItems(portlist)

# Scanning physical disks
hwmon = wmi.WMI()
disks = hwmon.Win32_DiskDrive()
for d in disks:
    disk_list.append(d.Caption)


# Apply button
def apply():
    check_checkboxes()
    if disk_selected:
        for disk in range(len(disk_selected)):
            selected.append(f'DiskSpace.{disk_selected[disk]}')
    if disk_selected_rw:
        for disk in range(len(disk_selected_rw)):
            selected.append(f'DiskUsage.{disk_selected_rw[disk]}')
    serialSendInt(make_selected_int())
    loop()
    QtTest.QTest.qWait(1000)
    loop()
    QtTest.QTest.qWait(1000)
    loop()


# The main cycle of sending data
def loop():
    global unsorted_data
    unsorted_data = organize_data()
    unsorted_data['destiny'] = 'data'

    # Send Info to Arduino
    serialSendDict(unsorted_data)


# Sending data to Arduino
def serialSendInt(data):
    if data[0] == 'info':
        data.pop(0)
        txs = '99,' + ','.join(map(str, data)) + ';'
        # print(txs)
        serial.write(txs.encode())


# Sending data to Arduino
def serialSendDict(data):
    if data['destiny'] == 'data':
        ints = make_selected_int()
        ints.pop(0)
        for int in ints:
            # QtTest.QTest.qWait(100)
            val = take_what_you_need(int)
            txs = int + ',' + ','.join(map(str, val)) + ';'
            # print(txs)
            serial.write(txs.encode())


# Make selected to int for Arduino
def make_selected_int():
    selected_int = ['info']

    if 'CPU' in selected:
        selected_int.append('1')
    if 'CPUClocks' in selected:
        selected_int.append('2')
    if 'GPU' in selected:
        selected_int.append('3')
    if 'GPUClocks' in selected:
        selected_int.append('4')
    if 'GPUmem' in selected:
        selected_int.append('5')
    if 'RAMuse' in selected:
        selected_int.append('6')
    if 'RAMmem' in selected:
        selected_int.append('7')
    if 'Uptime' in selected:
        selected_int.append('8')
    return selected_int


# Returns the data in the desired form
def take_what_you_need(sel):
    if sel == '1':
        return [unsorted_data.get('CPUTemp'), unsorted_data.get('CPULoad')]
    if sel == '2':
        return [unsorted_data.get('CPUClocks')]
    if sel == '3':
        return [unsorted_data.get('GPUTemp'), unsorted_data.get('GPULoad')]
    if sel == '4':
        return [unsorted_data.get('GPUClocks'), unsorted_data.get('GPUmemClocks')]
    if sel == '5':
        return [unsorted_data.get('GPUmem'), unsorted_data.get('GPUmemFree')]
    if sel == '6':
        return [unsorted_data.get('RAMuse')]
    if sel == '7':
        return [unsorted_data.get('RAMused'), unsorted_data.get('RAMfree')]
    if sel == '8':
        return [unsorted_data.get('Uptime')]


# Counting the number of pressed checkboxes
def check_checkboxes():
    global selected
    selected.clear()
    if ui.cpu.isChecked():
        selected.append('CPU')
    if ui.cpuclocks.isChecked():
        selected.append('CPUClocks')
    if ui.gpu.isChecked():
        selected.append('GPU')
    if ui.gpuclocks.isChecked():
        selected.append('GPUClocks')
    if ui.gpumem.isChecked():
        selected.append('GPUmem')
    if ui.ramuse.isChecked():
        selected.append('RAMuse')
    if ui.rammem.isChecked():
        selected.append('RAMmem')
    if ui.uptime.isChecked():
        selected.append('Uptime')
    return selected


# Disabling the ability to click checkboxes
def edit_checkboxes(state):
    if state == 'disable':
        if not ui.cpu.isChecked():
            ui.cpu.setCheckable(False)
        if not ui.cpuclocks.isChecked():
            ui.cpuclocks.setCheckable(False)
        if not ui.gpu.isChecked():
            ui.gpu.setCheckable(False)
        if not ui.gpuclocks.isChecked():
            ui.gpuclocks.setCheckable(False)
        if not ui.gpumem.isChecked():
            ui.gpumem.setCheckable(False)
        if not ui.ramuse.isChecked():
            ui.ramuse.setCheckable(False)
        if not ui.rammem.isChecked():
            ui.rammem.setCheckable(False)
        if not ui.uptime.isChecked():
            ui.uptime.setCheckable(False)
        if not ui.diskspace.isChecked():
            ui.diskspace.setCheckable(False)
        if not ui.diskusage.isChecked():
            ui.diskusage.setCheckable(False)
    if state == 'enable':
        ui.cpu.setCheckable(True)
        ui.cpuclocks.setCheckable(True)
        ui.gpu.setCheckable(True)
        ui.gpuclocks.setCheckable(True)
        ui.gpumem.setCheckable(True)
        ui.ramuse.setCheckable(True)
        ui.rammem.setCheckable(True)
        ui.uptime.setCheckable(True)
        ui.diskspace.setCheckable(True)
        ui.diskusage.setCheckable(True)


# Reading and counting clicks
def display(val):
    global count
    if val == 2 and count < 4:
        count += 1
        if count == 4:
            edit_checkboxes('disable')
    elif val == 0 and count <= 4:
        count -= 1
        if count == 3:
            edit_checkboxes('enable')


# Reading and counting clicks
def display_disks(val):
    global count
    global disk_selected
    if val in disk_list and count < 4:
        if val in disk_selected and count <= 4:
            disk_selected.remove(val)
            count -= 1
            if count == 3:
                edit_checkboxes('enable')
            return
        disk_selected.append(val)
        count += 1
        if count == 4:
            edit_checkboxes('disable')
    elif val == 0:
        count = count - len(disk_selected)
        if count != 4:
            edit_checkboxes('enable')
        disk_selected.clear()


# Reading and counting clicks
def display_disks_rw(val):
    global count
    global disk_selected_rw
    if val in disk_list and count < 4:
        if val in disk_selected:
            disk_selected_rw.remove(val)
            count -= 1
            if count == 3:
                edit_checkboxes('enable')
            return
        disk_selected_rw.append(val)
        count += 1
        if count == 4:
            edit_checkboxes('disable')
    elif val == 0:
        count = count - len(disk_selected_rw)
        if count != 4:
            edit_checkboxes('enable')
        disk_selected_rw.clear()


# Read Arduino port
def onRead():
    rx = serial.readLine()
    rxs = str(rx, 'utf-8').strip()
    data = rxs.split(',')
    # print(data)


# Open port button
def onOpen():
    serial.setPortName(ui.comlist.currentText())
    serial.open(QIODevice.ReadWrite)


# Close button
def close():
    serial.close()
    sys.exit(app.exec_())


# Checkboxes
ui.cpu.stateChanged.connect(display)
ui.cpuclocks.stateChanged.connect(display)
ui.gpu.stateChanged.connect(display)
ui.gpuclocks.stateChanged.connect(display)
ui.gpumem.stateChanged.connect(display)
ui.ramuse.stateChanged.connect(display)
ui.rammem.stateChanged.connect(display)
ui.uptime.stateChanged.connect(display)

# Combined boxes
ui.diskspace.stateChanged.connect(ui.combodiskspace.setEnabled)
ui.diskspace.stateChanged.connect(display_disks)
ui.combodiskspace.addItems(disk_list)
ui.combodiskspace.textActivated.connect(display_disks)
ui.diskusage.stateChanged.connect(ui.combodiskusage.setEnabled)
ui.diskusage.stateChanged.connect(display_disks_rw)
ui.combodiskusage.addItems(disk_list)
ui.combodiskusage.textActivated.connect(display_disks_rw)

# Buttons
ui.applybutton.clicked.connect(apply)
ui.exitbutton.clicked.connect(close)
ui.openbutton.clicked.connect(onOpen)

serial.readyRead.connect(onRead)

# Start UI
ui.show()
app.exec()
