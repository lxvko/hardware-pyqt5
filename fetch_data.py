import json
import time
from uptime import uptime
import requests
from pydantic import BaseModel

sensor_data = {
    "Load CPU Total": "",
    "Temperatures CPU Package": "",
    "Clocks CPU Core #1": "",
    "Clocks CPU Core #2": "",
    "Clocks CPU Core #3": "",
    "Clocks CPU Core #4": "",
    "Clocks CPU Core #5": "",
    "Clocks CPU Core #6": "",
    "Data Memory Used": "",
    "Data Memory Available": "",
    "Load Memory": "",
    "Temperatures GPU Core": "",
    "Clocks GPU Core": "",
    "Clocks GPU Memory": "",
    "Load GPU Core": "",
    "Data GPU Memory Total": "",
    "Data GPU Memory Used": "",
    "Uptime": "",
}


class data(BaseModel):
    Text: str
    Value: str


class Child2(BaseModel):
    Text: str
    Children: list[data]


class Child1(BaseModel):
    Text: str
    ImageURL: str
    Children: list[Child2]


class Child(BaseModel):
    Text: str
    Children: list[Child1]


class Computer(BaseModel):
    Children: list[Child]


url = 'http://localhost:8085/data.json'


def get_data():
    Uptime = time.strftime("%H:%M:%S", time.gmtime(uptime()))
    sensor_data['Uptime'] = Uptime

    response = requests.get(url=url)
    data = json.dumps(response.json(), indent=2)

    computer = Computer.parse_raw(data)
    parts = computer.Children[0].Children

    for part in parts:
        if part.ImageURL != 'images_icon/hdd.png':
            descriptions = part.Children
            for description in descriptions:
                if description.Text == 'Clocks':
                    datas = description.Children
                    for data in datas:
                        temp_data = f'Clocks {data.Text}'
                        if temp_data in sensor_data:
                            sensor_data[temp_data] = data.Value
                elif description.Text == 'Temperatures':
                    datas = description.Children
                    for data in datas:
                        temp_data = f'Temperatures {data.Text}'
                        if temp_data in sensor_data:
                            sensor_data[temp_data] = data.Value
                elif description.Text == 'Load':
                    datas = description.Children
                    for data in datas:
                        temp_data = f'Load {data.Text}'
                        if temp_data in sensor_data:
                            sensor_data[temp_data] = data.Value
                elif description.Text == 'Data':
                    datas = description.Children
                    for data in datas:
                        temp_data = f'Data {data.Text}'
                        if temp_data in sensor_data:
                            sensor_data[temp_data] = data.Value
        else:
            descriptions = part.Children
            for description in descriptions:
                if description.Text == 'Load':
                    datas = description.Children
                    for data in datas:
                        if data.Text == 'Used Space':
                            temp_data = f'Used Space {part.Text}'
                            sensor_data[temp_data] = data.Value
                if description.Text == 'Throughput':
                    datas = description.Children
                    for data in datas:
                        if data.Text == 'Read Rate':
                            temp_data = f'Read Rate {part.Text}'
                            sensor_data[temp_data] = data.Value
                        elif data.Text == 'Write Rate':
                            temp_data = f'Write Rate {part.Text}'
                            sensor_data[temp_data] = data.Value
    return sensor_data
