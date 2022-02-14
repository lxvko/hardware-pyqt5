from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5 import QtWidgets, uic, QtGui, QtTest
from PyQt5.QtCore import QIODevice
from uptime import uptime

import wmi
import sys
import time

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
infinity = 'not the limit'
hw_sensors = ['Temperature', 'Clock', 'Load', 'Data', 'SmallData', 'Throughput']
hw_names = ['Core Average', 'GPU Core', 'CPU Core #1', 'GPU Core', 'GPU Memory', 'CPU Total', 'GPU Core', 'Memory',
            'Memory Used', 'Memory Available', 'GPU Memory Used', 'GPU Memory Free', 'Used Space', 'Read Rate',
            'Write Rate']

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

# Preparation for parsing
hwmon = wmi.WMI()
disks = hwmon.Win32_DiskDrive()
hwmon = wmi.WMI(namespace="root/LibreHardwareMonitor")
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
    if count > 0:
        serialSendInt(make_selected_int())
        loop()


# The main cycle of sending data
def loop():
    while infinity == 'not the limit':
        global unsorted_data
        print_flag = ['print']
        QtTest.QTest.qWait(500)
        unsorted_data = organize_data()
        if unsorted_data is not None:
            unsorted_data['destiny'] = 'data'

            # Send Info to Arduino
            serialSendDict(unsorted_data)
            serialSendInt(print_flag)


# Sending data to Arduino
def serialSendInt(data):
    if data[0] == 'info':
        data.pop(0)
        txs = '99,' + ','.join(map(str, data)) + ';'
        serial.write(txs.encode())
    elif data[0] == 'print':
        data.pop(0)
        txs = '98,' + 'print' + ';'
        serial.write(txs.encode())
    elif data[0] == 'bye':
        data.pop(0)
        txs = '97,' + 'bye' + ';'
        serial.write(txs.encode())
    elif data[0] == 'hello':
        data.pop(0)
        txs = '95,' + ','.join(map(str, data)) + ';'
        serial.write(txs.encode())


# Sending data to Arduino
def serialSendDict(data):
    if data['destiny'] == 'data':
        ints = make_selected_int()
        ints.pop(0)
        for int in ints:
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
    try:
        if f'DiskSpace.{disk_list[0]}' in selected:
            selected_int.append('9')
    except IndexError:
        pass
    try:
        if f'DiskSpace.{disk_list[1]}' in selected:
            selected_int.append('10')
    except IndexError:
        pass
    try:
        if f'DiskSpace.{disk_list[2]}' in selected:
            selected_int.append('11')
    except IndexError:
        pass
    try:
        if f'DiskUsage.{disk_list[0]}' in selected:
            selected_int.append('12')
    except IndexError:
        pass
    try:
        if f'DiskUsage.{disk_list[1]}' in selected:
            selected_int.append('13')
    except IndexError:
        pass
    try:
        if f'DiskUsage.{disk_list[2]}' in selected:
            selected_int.append('14')
    except IndexError:
        pass

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
        return [unsorted_data.get('RAMused'), unsorted_data.get('RAMall')]
    if sel == '8':
        return ['Uptime: ' + unsorted_data.get('Uptime')]
    if sel == '9':
        return ['DiskSpace0: ' + unsorted_data.get('DiskUsedSpace[0]')]
    if sel == '10':
        return ['DiskSpace1: ' + unsorted_data.get('DiskUsedSpace[1]')]
    if sel == '11':
        return ['DiskSpace2: ' + unsorted_data.get('DiskUsedSpace[2]')]
    if sel == '12':
        return ['DiskRead0  ' + unsorted_data.get('DiskRead[0]'), 'DiskWrite0 ' + unsorted_data.get('DiskWrite[0]')]
    if sel == '13':
        return ['DiskRead1  ' + unsorted_data.get('DiskRead[1]'), 'DiskWrite1 ' + unsorted_data.get('DiskWrite[1]')]
    if sel == '14':
        return ['DiskRead2  ' + unsorted_data.get('DiskRead[2]'), 'DiskWrite2 ' + unsorted_data.get('DiskWrite[2]')]


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
    hello = ['hello', '95']
    QtTest.QTest.qWait(3000)
    serialSendInt(hello)


# Close button
def close():
    global infinity
    infinity = 'limit'
    bye = ['bye', '97']
    serialSendInt(bye)
    QtTest.QTest.qWait(1000)
    serial.close()
    sys.exit(app.exec_())


# Parsing a conventional sensor
def parse_sensor(Type, SensorName):
    sensors = hwmon.Sensor(SensorType=Type, Name=SensorName)
    for s in sensors:
        return round(s.Value, 2)


# Parsing >1 sensor
def parse_sensors(Type, SensorName):
    things = []
    sensors = hwmon.Sensor(SensorType=Type, Name=SensorName)
    if Type == 'Throughput':
        for s in sensors:
            things.append(human_bytes(s.Value))
            # things.append(s.Value)
    else:
        for s in sensors:
            thing = round(s.Value, 2)
            things.append(str(thing) + ' %')
    return things


# Data organization function
def organize_data():
    CPUTemp = parse_sensor(hw_sensors[0], hw_names[0])
    GPUTemp = parse_sensor(hw_sensors[0], hw_names[1])
    CPUClocks = parse_sensor(hw_sensors[1], hw_names[2])
    GPUClocks = parse_sensor(hw_sensors[1], hw_names[3])
    GPUmemClocks = parse_sensor(hw_sensors[1], hw_names[4])
    CPULoad = parse_sensor(hw_sensors[2], hw_names[5])
    GPULoad = parse_sensor(hw_sensors[2], hw_names[6])
    RAMuse = parse_sensor(hw_sensors[2], hw_names[7])
    RAMused = parse_sensor(hw_sensors[3], hw_names[8])
    RAMall = parse_sensor(hw_sensors[3], hw_names[9])
    RAMall = round(float(RAMall) + float(RAMused), 2)
    GPUmem = parse_sensor(hw_sensors[4], hw_names[10])
    GPUmemFree = parse_sensor(hw_sensors[4], hw_names[11])
    DiskUsedSpace = parse_sensors(hw_sensors[2], hw_names[12])
    DiskRead = parse_sensors(hw_sensors[5], hw_names[13])
    DiskWrite = parse_sensors(hw_sensors[5], hw_names[14])
    Uptime = time.strftime("%H:%M:%S", time.gmtime(uptime()))

    if len(DiskUsedSpace) > 1:
        hw_vars = {'CPUTemp': int(CPUTemp), 'GPUTemp': int(GPUTemp), 'CPUClocks': CPUClocks, 'GPUClocks': GPUClocks,
                   'GPUmemClocks': GPUmemClocks, 'CPULoad': int(CPULoad),
                   'GPULoad': int(GPULoad), 'RAMuse': int(RAMuse), 'RAMused': str(RAMused) + 'GB',
                   'RAMall': str(RAMall) + 'GB',
                   'GPUmem': int(GPUmem), 'GPUmemFree': int(GPUmemFree), 'Uptime': Uptime}
        for i in range(len(DiskUsedSpace)):
            hw_vars[f'DiskUsedSpace[{i}]'] = DiskUsedSpace[i]
        for i in range(len(DiskRead)):
            hw_vars[f'DiskRead[{i}]'] = DiskRead[i]
        for i in range(len(DiskWrite)):
            hw_vars[f'DiskWrite[{i}]'] = DiskWrite[i]
        return hw_vars


# Byte Conversion
def human_bytes(B):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)


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

if __name__ == '__main__':
    # Start UI
    ui.show()
    app.exec()
