# This is a sample Python script.
import flask
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from flask import Flask, jsonify
import json
import pickle
import requests
import pandas as pd
app = Flask(__name__)

load_model = pickle.load(open('model_weather.sav', 'rb'))
key = "&key=f38da8272f134341905d2f9724ae6c18"
cityInfo = [
    '{"id": "hcm", "name": "Hồ Chí Minh", "lat": 10.762622, "lon": 106.660172}',
    '{"id": "pt", "name": "Phan Thiết", "lat": 10.980460, "lon": 108.261477}',
    '{"id": "vt", "name": "Vũng Tàu", "lat": 10.502307, "lon": 107.169205}'
]
weatherInfo = [
    '{"id": "A", "name": "Nắng gắt", "icon": "https://e.unicode-table.com/orig/61/f16628bcdd145d6c40a13a2bda6047.png"}',
    '{"id": "B", "name": "Nắng", "icon": "https://e.unicode-table.com/orig/08/5de15fb08cd1abde620889c1161cc9.png"}',
    '{"id": "C", "name": "Nắng nhẹ", "icon": "https://e.unicode-table.com/orig/95/cc7993b2f440645560b4e2453e5ce1.png"}',
    '{"id": "D", "name": "Nhiều mây", "icon": "https://e.unicode-table.com/orig/b9/e3b0aa9c56af1aa2e501c41c9d3697.png"}',
    '{"id": "E", "name": "U ám", "icon": "https://e.unicode-table.com/orig/74/90ee256e6b65a64ae6afcfa5a437e2.png"}',
    '{"id": "F", "name": "Mưa rải rác", "icon": "https://e.unicode-table.com/orig/6e/fb6556a1ac9193099eb86ac2132bf6.png"}',
    '{"id": "G", "name": "Mưa nhiều rải rác", "icon": "https://e.unicode-table.com/orig/6e/fb6556a1ac9193099eb86ac2132bf6.png"}',
    '{"id": "H", "name": "Mưa và nhiều mây", "icon": "https://e.unicode-table.com/orig/cb/f8bb2e6efeea5a9ff034b91d2150ea.png"}',
    '{"id": "I", "name": "Mưa nhiều", "icon": "https://e.unicode-table.com/orig/12/3ec0ac0e091b2b1b00ebba337e548d.png"}',
]
week = {"0": "Thứ hai", "1": "Thứ ba", "2": "Thứ tư", "3": "Thứ năm", "4": "Thứ sáu", "5": "Thứ bảy", "6": "Chủ nhật"}

def callLabelWeather(lbl):
    for i in weatherInfo:
        j = json.loads(i)
        if str(j["id"]) == str(lbl):
            return [str(j["name"]), str(j["icon"])]
    return []
def callWeather(lat, lon):
    urls = "https://api.weatherbit.io/v2.0/forecast/daily?&lat="+str(lat)+"&lon="+str(lon)+"&key=32555f07f8a844059cda3d2e62bacd44"
    response = requests.get(urls)
    data = []
    for i in response.json()["data"]:
        predict = load_model.predict([[float(i["max_temp"])/100,
                                       float(i["min_temp"])/100,
                                       float(i["wind_spd"])/100,
                                       float(i["wind_dir"])/360,
                                       float(i["rh"])/100,
                                       float(i["clouds"])/100]])
        weather = callLabelWeather(predict[0])
        date = '"date": "' + str(i["datetime"]) + '",'
        day = '"day": "' + week[str(pd.Timestamp(str(i["datetime"])).dayofweek)] + '",'
        temp_max = '"temp_max": ' + str(i["max_temp"]) + ','
        temp_min = '"temp_min": ' + str(i["min_temp"]) + ','
        wind_spd = '"wind_spd": ' + str(i["wind_spd"]) + ','
        wind_dir = '"wind_dir": ' + str(i["wind_dir"]) + ','
        hum = '"hum": ' + str(i["rh"]) + ','
        cld = '"cld": ' + str(i["clouds"]) + ','
        name = '"name": "' + str(weather[0]) + '",'
        icon = '"icon": "' + str(weather[1]) + '"'
        dt = '{'+date+day+temp_max+temp_min+wind_spd+wind_dir+hum+cld+name+icon+'}'
        data.append(json.loads(dt))
    return data

@app.route("/api/v1/weather/city/<string:city_id>", methods=["GET"])
def getWeather(city_id) :
    for i in cityInfo:
        j = json.loads(i)
        if j["id"] == city_id:
            data = callWeather(j["lat"], j["lon"])
            return jsonify({"data" : data})
    return jsonify({"data" : ""})

@app.route("/api/v1/weather/<string:temp_max>/<string:temp_min>/<string:wind>/<string:windd>/<string:hum>/<string:cld>", methods=["GET"])
def guessWeather(temp_max, temp_min, wind, windd, hum, cld) :

    predict = load_model.predict([[float(temp_max) / 100 ,
                                   float(temp_min) / 100 ,
                                   float(wind) / 100 ,
                                   float(windd) / 360 ,
                                   float(hum) / 100 ,
                                   float(cld) / 100]])
    weather = callLabelWeather(predict[0])

    return jsonify({"data" : weather[1]})

@app.route("/api/v1/weather/lbl/<string:lbl>", methods=["GET"])
def getLabelWeather(lbl) :
    return jsonify({"data" : callLabelWeather(lbl)})

if __name__ == '__main__':
    app.run()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
