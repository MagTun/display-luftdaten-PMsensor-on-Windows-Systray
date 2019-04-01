################### In brief
# Connect to lufdatent PM sensor and get the value from the JSON url.
# Display the PM10/PM2.5 value in an icon in systray and update it when new value is available 
# Possible to have the value spoken by a voice engine  (cf menu of the systray icon)
# Possible to have a pop up notification cf ToastNotifier (need to be uncommented)

################### Ressources
# Luftdaten PM sensor = https://luftdaten.info/
# text to speech =  https://stackoverflow.com/a/48438829/3154274
# request retry = https://stackoverflow.com/a/35504626/3154274
# url to json = https://stackoverflow.com/a/17517598/3154274
# text to image : Pillow (https://pillow.readthedocs.io/en/latest/handbook/tutorial.html - simple code sample:  https://code-maven.com/create-images-with-python-pil-pillow)
# icon in systray : infi.systray (https://github.com/Infinidat/infi.systray and https://stackoverflow.com/a/54082417/3154274)
###################


# works with ahk : https://www.autohotkey.com/  to unmute the computer
# to install Pillow (cf "from PIL" below):   pip install Pillow

from time import sleep

# connect to the json url
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

#process the json
import json

#call ahk needed to unmute computer
import subprocess

# voice (text to speech)
import pyttsx3

#for the script path (needed for setting working directory and  ToastNotifier)
import os

# get script path to set working directory + quit the script when click on "Quit" in systray menu
import sys

# from win10toast import ToastNotifier   # replaced by icon in systray

# icon in systray
from infi.systray import SysTrayIcon

# text to icon
from PIL import Image, ImageDraw, ImageFont


# create a .ico image with the PM10 value
def create_image(text1, text2, colortext=(0, 0, 0), coord=(0, 0)):
    img = Image.new('RGB', (50, 50), pmwatch.iconcolorbackground)  # create a 50*50 image
    # create a drawable layer
    d = ImageDraw.Draw(img)
    # if the script is unmute, draw a red rectangle on the bottom right corner
    if pmwatch.sound == True:
        # coordinate of rectangle [(x0,y0),(y1,y1)] -  color = red
        d.rectangle([(35, 35), (50, 50)], fill=(255, 0, 0), outline=None)

    # set font + size of the text
    font_type10 = ImageFont.truetype("arial.ttf", 30)
    d.text(coord, text1, colortext, font=font_type10)   # write the text
    font_type25 = ImageFont.truetype("arial.ttf", 25)
    d.text((1,26), text2, colortext, font=font_type25)   # write the text
    img.save(pmwatch.iconname)  # save the image
    icon_size=[(16,16)]
    img.save(pmwatch.iconname, sizes=icon_size) 
    # img.show() #● 

# def called by def unmute and def mute : send the right argument to the def create_image - if PM value too high, text in red
def update_image_systray(systray):
    if pmwatch.pm10_rounded > 5:
        create_image(f"{pmwatch.pm10_rounded}",f"{pmwatch.pm25_rounded}", (255, 0, 0))
    else:
        create_image(f"{pmwatch.pm10_rounded}",f"{pmwatch.pm25_rounded}" )
    systray.update(icon=pmwatch.iconname)

#def called by systray to unmute (create a new image without a red rectangle)
def unmute(systray):
    pmwatch.sound = True
    update_image_systray(systray) 

#def called by systray to mute (create a new image with  a red rectangle)
def mute(systray):
    pmwatch.sound = False
    update_image_systray(systray)  

#speak the value of PM10
def speak(engine, value):
    value_as_str = str(value)
    engine.say(value_as_str + "...")
    engine.runAndWait()
    # when speak add "+" after the value printed
    print("+", end="", flush=True)  # "end" and "flush" = do not close the line






# quit the script when click on "Quit" in systray menu
def on_quit_callback(systray):
    sys.exit()

# main function


def pmwatch(url, voiceengine, iconcolorbackground, iconname, icontext):
    ##### custom VAR
    path_ahk_exe = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'  # ★
    path_ahk_script_unmute = r'unmute sound.ahk'  # ★
    path_ahk_script_countdown = r'countdown on mouse.ahk'  # ★

    #### other VAR
    # need to get value from the PM on the first check because we use a delay on the following check
    not_first_time = False

    #set working directory to the script folder
    os.chdir(sys.path[0])

    #start the script with sound on
    pmwatch.sound = True

    # var needed to be able to use the argument in the other defs (ex mute)
    pmwatch.iconname = iconname
    pmwatch.iconcolorbackground = iconcolorbackground

    #### end of VAR

    #ToastNotifier : not used, replaced by systray icon
    # script_name=os.path.basename(__file__)  # needed for ToastNotifier title
    # toaster = ToastNotifier()

    # unmute sound of computer with ahk script and put volume to high
    subprocess.call([path_ahk_exe, path_ahk_script_unmute])

    #start text reader engine with the choosen voiceengine
    engine = pyttsx3.init(driverName='sapi5')
    engine.setProperty('voice', voiceengine)
    engine.setProperty('rate', 100)
    engine.setProperty('volume', 1)

    #create icon in systray at start up - it makes it easier to use systray.update() later on
    create_image(icontext, "")
    menu_options = (("Mute", None, mute), ("Unmute", None, unmute))
    systray = SysTrayIcon(iconname, icontext, menu_options,
                          on_quit=on_quit_callback)
    systray.start()

    while True:
        # connect to sensor and retrieve the data as dico
        s = requests.Session()
        retries = Retry(total=15, backoff_factor=1, status_forcelist=[
                        500, 502, 503, 504])  # delay=3,
        s.mount('http://', HTTPAdapter(max_retries=retries))
        response = s.get(url)
        data = response.json()

        # if we resquest json too early (except for first connection), add some delay to wait for the new  PM value
        if float(data['age']) > 15 and not_first_time:
            time_to_wait = 146 - round(float(data['age']))
            print(f"waiting time (delayed): {time_to_wait} s.")
            sleep(time_to_wait)  # Time in seconds

        # process the new value
        else:
            # save the needed values
            pm10 = data['sensordatavalues'][0]['value']
            pm25 = data['sensordatavalues'][1]['value']
            temper = data['sensordatavalues'][2]['value']
            humid = data['sensordatavalues'][3]['value']
            pmwatch.pm10_rounded = round(float(pm10))
            pmwatch.pm25_rounded = round(float(pm25))


            #print the new values
            print(
                f"\t \t \t \t PM10: {pm10}   PM2.5: {pm25} Temp: {temper} Hum: {humid}", end="", flush=True)

            #speak the pm10 value only if sound is unmute
            if pmwatch.sound:
                
                speak(engine, pmwatch.pm10_rounded)

            #add a line break  (we use no carriage for when printing value + in speak()  )
            print("")  # add the linebreak

            # create the icon for systray + update image
            update_image_systray(systray)

            # toaster.show_toast(script_name,
            #             f"Pm10 = {pm10}\nPm25 = {pm25}",
            #             icon_path=r".....",  #★
            #             duration=5)

            # after the first run, add the delay when we check to be sure we get a new value.
            not_first_time = True

            #time to wait before checking again for a new value
            # 143 = 145 -2 sec as random delay (if use ToastNotifier, remove again 5 sec for the pop up so : 138)
            time_to_wait = 143 - round(float(data['age']))
            print(
                f"Waiting time (in sec - start = {time_to_wait} ):   {time_to_wait}", end="", flush=True)

            # print remaining time before next check :  update the remaining time every second
            while time_to_wait > 1:
                if time_to_wait == 100:
                    # need a space after \b to "replace the cursor where it was"
                    print("\b\b\b ", end="", flush=True)
                elif time_to_wait == 10:
                    print("\b\b ", end="", flush=True)
                else:
                    for i in range(len(str(time_to_wait))):
                        print("\b", end="", flush=True)
                time_to_wait = time_to_wait-1
                print(time_to_wait, end="", flush=True)
                sleep(1)
            print("")

            # display a count down next to the mouse (but disturbing because there is a delay when we move the mouse)
            # python will wait for the ahk script to finish before moving on.
            # if used, need to comment the  whole "while time_to_wait > 1"
            # subprocess.call([path_ahk_exe, path_ahk_script_countdown, str(time_to_wait)])


# ●  needed to test (it works by running this script)
if __name__ == "__main__":
    ###### Int:
    url = 'http://192.168.1.15/data.json'
    voiceengine = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
    # Other Windows voice = HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0

    # blue: (125, 167, 242)   pink (242, 142, 238)
    iconcolorbackground = (242, 142, 238)
    iconname = 'a.ico'
    icontext = 'In'
    pmwatch(url, voiceengine, iconcolorbackground, iconname, icontext)
