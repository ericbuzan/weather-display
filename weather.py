#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import Image, ImageFont, ImageDraw
import json
import time
import requests
import os
import sys

BLACK = 0

print(os.getcwd())
if os.getcwd() == '/weather':
    print('change!')
    os.chdir('../')
    os.getcwd()

huge_font = ImageFont.truetype('Roboto-Regular.ttf',120)
big_font = ImageFont.truetype('Roboto-Regular.ttf',64)
bigish_font = ImageFont.truetype('RobotoCondensed-Regular.ttf',64)
large_font = ImageFont.truetype('Roboto-Regular.ttf',36)
largeish_font = ImageFont.truetype('RobotoCondensed-Regular.ttf',36)
normal_font = ImageFont.truetype('Roboto-Regular.ttf',28)
normalish_font = ImageFont.truetype('RobotoCondensed-Regular.ttf',28)
small_font = ImageFont.truetype('Roboto-Regular.ttf',18)
tiny_font = ImageFont.truetype('Roboto-Regular.ttf',12)

big_weather_font = ImageFont.truetype('weathericons-regular-webfont.ttf',225)
small_weather_font = ImageFont.truetype('weathericons-regular-webfont.ttf',125)

icons = {
    'clear-day': '\uf00d',
    'clear-night': '\uf02e',
    'rain': '\uf019',
    'snow': '\uf01b',
    'sleet': '\uf0b5',
    'wind': '\uf050',
    'fog': '\uf014',
    'cloudy': '\uf013',
    'partly-cloudy-day': '\uf002',
    'partly-cloudy-night': '\uf086',
    'hail': '\uf015',
    'thunderstorm': '\uf01e',
    'tornado': '\uf056'
}
def make_weather():

    def draw_center(pos,text,font):
        px,py,sx,sy = pos
        w,h = draw.textsize(text,font=font)
        if sx == 0:
            w = 0
        if sy == 0:
            h = 0
        draw.text(((sx-w)/2+px,(sy-h)/2+py),text,BLACK,font=font)

    def draw_right(pos,text,font):
        px,py = pos
        w,h = draw.textsize(text,font=font)
        draw.text((px-w,py),text,BLACK,font=font)

    out_image = Image.new('L',(600,800),(255))
    draw = ImageDraw.Draw(out_image)



    get_fresh_data = False

    with open('data/options.json') as optfile:
        options = json.load(optfile)

    api_key = options['api_key']
    lat = options['lat']
    lon = options['lon']

    try:
        with open('weatherdata.json','r') as infile:
            weather = json.load(infile)
        update_time = weather['currently']['time']
        current_time = time.time()
        if current_time - 60*10 > update_time:
            print('Old data out of date, updating')
            get_fresh_data = True
        else:
            pass
            #print('Old data still good')
    except FileNotFoundError:
            print('No old data found! Getting new...')
            get_fresh_data = True


    if get_fresh_data:
        weather_response = requests.get(f'https://api.darksky.net/forecast/{api_key}/{lat},{lon}')
        try:
            weather = weather_response.json()
        except:
            print('ERROR! Fix your api key or location nerd')
            sys.exit(1)
        with open('weatherdata.json','w') as outfile:
            json.dump(weather,outfile,sort_keys=True,indent=4) 


    date_text = time.strftime('%A, %B %d, %Y',time.localtime())
    draw.text((10,10),date_text,font=large_font)

    time_text = time.strftime('%I:%M %p',time.localtime())
    draw_right((590,10),time_text,large_font)

    temp = round(float(weather['currently']['temperature']))
    draw.text((330,70),f'{temp}°F',BLACK,font=huge_font)

    condition = weather['currently']['icon']
    condition_icon = icons[condition]
    draw_center((0,50,340,300),condition_icon,big_weather_font)
    # for icon in icons.values():
    #     draw_center((0,50,330,300),icon,big_weather_font)

    feels_like = round(weather['currently']['apparentTemperature'])
    draw.text((340,210),f'Feels Like: {feels_like}°F',BLACK,font=normal_font)

    DIRECTIONS = ['N','NE','E','SE','S','SW','W','SW']
    wind_degree_idx = ((weather['currently']['windBearing']+22) % 360) // 45
    wind_dir = DIRECTIONS[wind_degree_idx]
    wind_speed = round(float(weather['currently']['windSpeed']))
    if wind_speed == 0:
        draw.text((340,250),'Wind: Calm',BLACK,font=normal_font)
    else:
        draw.text((340,250),f'Wind: {wind_dir} {wind_speed} mph',BLACK,font=normal_font)

    humidity = int(weather['currently']['humidity'] * 100)
    draw.text((340,290),f'Humidity: {humidity}%',BLACK,font=normal_font)

    pressure = round(weather['currently']['pressure'])
    draw.text((340,330),f'Pressure: {pressure} mbar',BLACK,font=normalish_font)


    threeday_forecast = weather['daily']['data'][0:3]

    for i,day_cast in enumerate(threeday_forecast):

        shift = 200*i

        forecast_time = day_cast['time']
        day_text = time.strftime('%A',time.localtime(forecast_time))
        draw_center((shift,400,200,0),day_text,large_font)

        condition = day_cast['icon']
        forecast_icon = icons[condition]
        draw_center((shift,415,200,200),forecast_icon,small_weather_font)
        # for icon in icons.values():
        #     draw_center((shift,415,200,200),icon,small_weather_font)

        hi_temp = round(day_cast['temperatureMax'])
        draw.text((shift+25,610),"High",BLACK,font=small_font)
        draw.text((shift+35,625),f"{hi_temp}°F",BLACK,font=big_font)

        low_temp = round(day_cast['temperatureMin'])
        draw.text((shift+25,690),"Low",BLACK,font=small_font)
        draw.text((shift+35,705),f"{low_temp}°F",BLACK,font=big_font)

        draw.line((200+shift,410,200+shift,770),BLACK,width=2)


    update_time = weather['currently']['time']
    now_time = time.strftime('Updated %I:%M %p',time.localtime(update_time))
    draw.text((5,782),now_time,BLACK,font=tiny_font)


    out_image.save('./weather/weather.png')
    #out_image.show()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'repeat':
            print('Running on repeat...')
            while True:
                print(time.strftime('Making a new image at %H:%M'))
                make_weather()
                time.sleep(2)
                print('Waiting until next minute...')
                while time.localtime().tm_sec != 0:
                    time.sleep(.5)
    print('Running once...')
    make_weather()

