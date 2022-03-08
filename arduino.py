from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from PyQt5 import QtTest

serial = QSerialPort()
serial.setBaudRate(115200)
disk_list = []
selected = []


# Configuring the Arduino Port
def get_ports():
    portlist = []
    ports = QSerialPortInfo().availablePorts()
    for port in ports:
        portlist.append(port.portName())
    return portlist


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
    ints = make_selected_int(selected, disk_list)
    ints.pop(0)
    for int in ints:
        val = take_what_you_need(int, data)
        print(val)
        txs = int + ',' + ','.join(map(str, val)) + ';'
        serial.write(txs.encode())


# Open port button
def onOpen(port):
    serial.setPortName(port)
    serial.open(QIODevice.ReadWrite)
    hello = ['hello', '95']
    QtTest.QTest.qWait(3000)
    serialSendInt(hello)


# Make selected to int for Arduino
def make_selected_int(sel, disks):
    global disk_list
    global selected
    selected = sel
    disk_list = disks

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
        if f'Disk Space {disks[0]}' in selected:
            selected_int.append('9')
    except IndexError:
        pass
    try:
        if f'Disk Space {disks[1]}' in selected:
            selected_int.append('10')
    except IndexError:
        pass
    try:
        if f'Disk Space {disks[2]}' in selected:
            selected_int.append('11')
    except IndexError:
        pass
    try:
        if f'Disk Usage {disks[0]}' in selected:
            selected_int.append('12')
    except IndexError:
        pass
    try:
        if f'Disk Usage {disks[1]}' in selected:
            selected_int.append('13')
    except IndexError:
        pass
    try:
        if f'Disk Usage {disks[2]}' in selected:
            selected_int.append('14')
    except IndexError:
        pass

    return selected_int


# Returns the data in the desired form
def take_what_you_need(sel, data):
    match sel:
        case '1':
            return [data.get('Temperatures CPU Package'),
                    data.get('Load CPU Total')]
        case '2':
            return [data.get('Clocks CPU Core #1')]
        case '3':
            return [data.get('Temperatures GPU Core'),
                    data.get('Load GPU Core')]
        case '4':
            return [data.get('Clocks GPU Core'),
                    data.get('Clocks GPU Memory')]
        case '5':
            return [data.get('Data GPU Memory Used'),
                    data.get('Data GPU Memory Total')]
        case '6':
            return [data.get('Load Memory')]
        case '7':
            return [data.get('Data Memory Used'),
                    data.get('Data Memory Available')]
        case '8':
            return ['Uptime: ' + data.get('Uptime')]
        case '9':
            return ['DiskSpace0: ' + data.get(f'Used Space {disk_list[0]}')]
        case '10':
            return ['DiskSpace1: ' + data.get(f'Used Space {disk_list[1]}')]
        case '11':
            return ['DiskSpace2: ' + data.get(f'Used Space {disk_list[2]}')]
        case '12':
            return ['DiskRead0  ' + data.get(f'Read Rate {disk_list[0]}'),
                    'DiskWrite0 ' + data.get(f'Write Rate {disk_list[0]}')]
        case '13':
            return ['DiskRead1  ' + data.get(f'Read Rate {disk_list[1]}'),
                    'DiskWrite1 ' + data.get(f'Write Rate {disk_list[1]}')]
        case '14':
            return ['DiskRead2  ' + data.get(f'Read Rate {disk_list[2]}'),
                    'DiskWrite2 ' + data.get(f'Write Rate {disk_list[2]}')]


if __name__ == "__main__":
    pass
