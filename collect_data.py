from uptime import uptime

import time
import wmi

hw_sensors = ['Temperature', 'Clock', 'Load', 'Data', 'SmallData', 'Throughput']
hw_names = ['Core Average', 'GPU Core', 'CPU Core #1', 'GPU Core', 'GPU Memory', 'CPU Total', 'GPU Core', 'Memory',
            'Memory Used', 'Memory Available', 'GPU Memory Used', 'GPU Memory Free', 'Used Space', 'Read Rate',
            'Write Rate']

hwmon = wmi.WMI(namespace="root/LibreHardwareMonitor")


def parse_sensor(Type, SensorName):
    sensors = hwmon.Sensor(SensorType=Type, Name=SensorName)
    for s in sensors:
        return round(s.Value, 3)


def parse_sensors(Type, SensorName):
    things = []
    sensors = hwmon.Sensor(SensorType=Type, Name=SensorName)
    if Type == 'Throughput':
        for s in sensors:
            # things.append(human_bytes(s.Value))
            things.append(s.Value)
    else:
        for s in sensors:
            thing = round(s.Value, 2)
            things.append(str(thing) + ' %')
    return things


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
    RAMfree = parse_sensor(hw_sensors[3], hw_names[9])
    GPUmem = parse_sensor(hw_sensors[4], hw_names[10])
    GPUmemFree = parse_sensor(hw_sensors[4], hw_names[11])
    DiskUsedSpace = parse_sensors(hw_sensors[2], hw_names[12])
    DiskRead = parse_sensors(hw_sensors[5], hw_names[13])
    DiskWrite = parse_sensors(hw_sensors[5], hw_names[14])
    Uptime = time.strftime("%H:%M:%S", time.gmtime(uptime()))

    if len(DiskUsedSpace) > 1:
        hw_vars = {'CPUTemp': CPUTemp, 'GPUTemp': GPUTemp, 'CPUClocks': CPUClocks, 'GPUClocks': GPUClocks,
                   'GPUmemClocks': GPUmemClocks, 'CPULoad': CPULoad,
                   'GPULoad': GPULoad, 'RAMuse': RAMuse, 'RAMused': RAMused, 'RAMfree': RAMfree,
                   'GPUmem': GPUmem, 'GPUmemFree': GPUmemFree, 'Uptime': Uptime}
        for i in range(len(DiskUsedSpace)):
            hw_vars[f'DiskUsedSpace[{i}]'] = DiskUsedSpace[i]
        for i in range(len(DiskRead)):
            hw_vars[f'DiskRead[{i}]'] = DiskRead[i]
        for i in range(len(DiskWrite)):
            hw_vars[f'DiskWrite[{i}]'] = DiskWrite[i]
        return hw_vars


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


if __name__ == '__main__':
    print(organize_data())
    pass

# to_print = (f'CPUTemp = {CPUTemp} C\n'
#             f'GPUTemp = {GPUTemp} C\n'
#             f'CPUClocks = {CPUClocks} MHz\n'
#             f'GPUClocks = {GPUClocks} MHz\n'
#             f'GPUmemClocks = {GPUmemClocks} MHz\n'
#             f'CPULoad = {CPULoad} %\n'
#             f'GPULoad = {GPULoad} %\n'
#             f'RAMuse = {RAMuse} %\n'
#             f'RAMused = {RAMused} GB\n'
#             f'RAMfree = {RAMfree} GB\n'
#             f'GPUmem = {GPUmem} MB\n'
#             f'GPUmemFree = {GPmemFree} MB\n'
#             f'Uptime = {Uptime} \n'
#             f'DiskUsedSpace = {DiskUsedSpace} \n'
#             f'DiskRead = {DiskRead} \n'
#             f'DiskWrite = {DiskWrite} \n')