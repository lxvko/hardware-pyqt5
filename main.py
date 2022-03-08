from PyQt5 import QtWidgets, uic, QtGui, QtTest
from arduino import serialSendInt, serialSendDict, onOpen
from arduino import get_ports, make_selected_int
from fetch_data import get_data

import wmi
import sys

# The value of the selected ones
# cpu               1     - CPU                - CPUTemp, CPULoad
# cpuclocks         2     - CPUClocks          - CPUClocks
# gpu               3     - GPU                - GPUTemp, GPULoad
# gpuclocks         4     - GPUClocks          - GPUClocks, GPUmemClocks
# gpumem            5     - GPUmem             - GPUmem, GPUmemAll
# ramuse            6     - RAMuse             - RAMuse
# rammem            7     - RAMmem             - RAMused, RAMall
# uptime            8     - Uptime             - Uptime
# diskspace0123...  9     - DiskSpace.DiskName - DiskUsedSpace[i]
# diskusage0123...  10    - DiskUsage.DiskName - DiskRead[i], DiskWrite[i]

# Variables
count = 0
selected = []
disk_list = []
disk_selected = []
disk_selected_rw = []
data = {}

infinity = 'not the limit'


# Launching the UI
app = QtWidgets.QApplication([])
ui = uic.loadUi('etc/hwmon.ui')
ui.setWindowIcon(QtGui.QIcon('etc/icon.jpg'))
ui.comlist.addItems(get_ports())


# Preparation for parsing
hwmon = wmi.WMI()
disks = hwmon.Win32_DiskDrive()
for d in disks:
    disk_list.append(d.Caption)


# Apply button
def apply():
    check_checkboxes()
    if disk_selected:
        for disk in range(len(disk_selected)):
            selected.append(f'Disk Space {disk_selected[disk]}')
    if disk_selected_rw:
        for disk in range(len(disk_selected_rw)):
            selected.append(f'Disk Usage {disk_selected_rw[disk]}')
    if count > 0:
        # Sending labels to Arduino
        serialSendInt(make_selected_int(selected, disk_list))
        # Main cycle
        loop()


# The main cycle of sending data
def loop():
    while infinity == 'not the limit':
        QtTest.QTest.qWait(999)
        data = get_data()
        if data is not None:
            # Send Data to Arduino
            serialSendDict(data)
            # Send Print Flag to Arduino
            serialSendInt(['print'])


# Close button
def close():
    global infinity

    infinity = 'limit'
    bye = ['bye', '97']
    serialSendInt(bye)

    QtTest.QTest.qWait(1000)
    sys.exit(app.exec_())


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
        if val in disk_selected_rw:
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


def Open():
    onOpen(ui.comlist.currentText())


# Checkboxes
ui.cpu.stateChanged.connect(display)
ui.cpu.setToolTip('Выводится температура и загрузка ЦП')
ui.cpuclocks.stateChanged.connect(display)
ui.cpuclocks.setToolTip('Выводится текущая частота ЦП')
ui.gpu.stateChanged.connect(display)
ui.gpu.setToolTip('Выводится температура и загрузка ГП')
ui.gpuclocks.stateChanged.connect(display)
ui.gpuclocks.setToolTip('Выводится текущая частота ядра и частота памяти ГП')
ui.gpumem.stateChanged.connect(display)
ui.gpumem.setToolTip('Выводится информация об используемой видеопамяти')
ui.ramuse.stateChanged.connect(display)
ui.ramuse.setToolTip('Выводится информация об используемой ОЗУ графически')
ui.rammem.stateChanged.connect(display)
ui.rammem.setToolTip('Выводится информация об используемой ОЗУ')
ui.uptime.stateChanged.connect(display)
ui.uptime.setToolTip('Выводится время работы компьютера с момента включения')

# Combined boxes
ui.diskspace.setToolTip('Выводится информация о занимаемом пространстве диска')
ui.diskspace.stateChanged.connect(ui.combodiskspace.setEnabled)
ui.diskspace.stateChanged.connect(display_disks)
ui.combodiskspace.addItems(disk_list)
ui.combodiskspace.textActivated.connect(display_disks)
ui.diskusage.setToolTip('Выводится информация о текущей скорости записи и чтения диска')
ui.diskusage.stateChanged.connect(ui.combodiskusage.setEnabled)
ui.diskusage.stateChanged.connect(display_disks_rw)
ui.combodiskusage.addItems(disk_list)
ui.combodiskusage.textActivated.connect(display_disks_rw)

# Buttons
ui.applybutton.clicked.connect(apply)
ui.exitbutton.clicked.connect(close)
ui.openbutton.clicked.connect(Open)

if __name__ == '__main__':
    # Start UI
    ui.show()
    app.exec()
