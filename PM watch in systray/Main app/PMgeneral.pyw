# In brief
# Connect to lufdatent PM sensor and get the value from the JSON url.
# Display the PM10/PM2.5 value in an icon in systray and update it when new value is available
# Possible to have the value spoken aloud by a voice engine  (cf menu of the systray icon)
# Possible to have a pop up notification cf ToastNotifier (need to be uncommented)

# cf notice at https://github.com/MagTun/luftdaten-stuff


from time import sleep

# connect to the json url
import requests

# process the json
import json

# call ahk needed to unmute computer
import subprocess


# to set temp max
import easygui

# for the script path (needed for setting working directory and ToastNotifier)
import os

# get script path to set working directory + quit the script when click on "Quit" in systray menu
import sys

# from win10toast import ToastNotifier   # replaced by icon in systray

# icon in systray 
from infi.systray import SysTrayIcon

# text to icon
from PIL import Image, ImageDraw, ImageFont

# create HTML alert if temperature too high / bug
import traceback
import datetime
import webbrowser

# optional : add the GMAIL API to create alert (we need first to add the module folder to path so we can import it
try:
     # if needed 
    # sys.path.append(r"C:\Users\<user>\Desktop\Script\python\Google API\send email")
    from gmailAPI import sendemail
except:
    pass

# optional: voice (text to speech)
try:
    import pyttsx3
except:
    pass


# create a .ico image with the PM10 value
def create_image(text1, text2, colortext=(0, 0, 0), coord=(0, 0)):

    # create a 50*50 image
    img = Image.new('RGB', (50, 50), pmwatch.iconcolorbackground)
    # create a drawable layer
    d = ImageDraw.Draw(img)
    # if the script is unmute, draw a red rectangle on the bottom right corner
    if pmwatch.texttospeech == "on":
        # coordinate of rectangle [(x0,y0),(y1,y1)] -  color = red
        d.rectangle([(35, 35), (50, 50)], fill=(255, 0, 0), outline=None)
    if pmwatch.connection_error == True:
        # *5 = range(10) in retry when connection failed
        x = 50 - pmwatch.connection_retry * 5
        y = pmwatch.connection_retry * 5
        d.rectangle([(x, 0), (50, y)], fill=(255, 242, 0), outline=None)

    # set font + size of the text
    # ●  gif no pm2.5 then replace 30 by 35
    font_type10 = ImageFont.truetype("arial.ttf", 30)
    d.text(coord, text1, colortext, font=font_type10)   # write the value pm10
    font_type25 = ImageFont.truetype("arial.ttf", 25)
    # write the value pm2.5
    d.text((1, 26), text2, colortext, font=font_type25)
    # img.save(pmwatch.iconname)  # save the image
    icon_size = [(16, 16)]
    img.save(pmwatch.iconname, sizes=icon_size)
    # img.show() #●

# def called by def unmute and def mute : send the right argument to the def create_image - if PM value too high, text in red


def update_image_systray(systray):
    if pmwatch.connection_error == 2:
        create_image("X", "X")
    elif pmwatch.pm10_rounded > 5:
        create_image(f"{pmwatch.pm10_rounded}",
                     f"{pmwatch.pm25_rounded}", (255, 0, 0))
    else:
        create_image(f"{pmwatch.pm10_rounded}",
                     f"{pmwatch.pm25_rounded}", )
    if pmwatch.texttospeech == "on":
        systray.update(icon=pmwatch.iconname,
                       menu_options=pmwatch.menu_options_mute)
    elif pmwatch.texttospeech == "off":
        systray.update(icon=pmwatch.iconname,
                       menu_options=pmwatch.menu_options_unmute)
    else:
        systray.update(icon=pmwatch.iconname,
                       menu_options=pmwatch.menu_options_notexttospeech)


# def called by systray to unmute (create a new image without a red rectangle)
def unmute(systray):
    pmwatch.texttospeech = "on"
    update_image_systray(systray)
    # unmute sound of computer with ahk script and put volume to high
    subprocess.call([pmwatch.path_ahk_exe, pmwatch.path_ahk_script_unmute])


# def called by systray to mute (create a new image with  a red rectangle)
def mute(systray):
    pmwatch.texttospeech = "off"
    update_image_systray(systray)


# speak the value of PM10
def speak(engine, value):
    value_as_str = str(value)
    engine.say(value_as_str + "...")
    engine.runAndWait()
    # when speak add "+" after the value printed
    print("+", end="", flush=True)  # "end" and "flush" = do not close the line


# def displaydata(systray):
#     webbrowser.open(pmwatch.url)  # Go to example.co


# set max temp
def settempmaxMessage(tempmax_var, message_out):
    # this def is called by settempmax : needed to prevent repeat of everything for  tempmax_out and tempmax_in

    message = f"Enter max temp for alert current temp={pmwatch.temper}  {message_out}"
    value = easygui.enterbox(
        msg=message, title=' ', default=tempmax_var, strip=True)
    try:
        if pmwatch.icontext == "Out":
            pmwatch.tempmax_out = int(value)
        if pmwatch.icontext == "In":
            pmwatch.tempmax_in = int(value)
    except:
        pass


def settempmax(systray):
    if pmwatch.icontext == "Out":
        settempmaxMessage(pmwatch.tempmax_out, "(max temp = 50° C)")
    if pmwatch.icontext == "In":
        settempmaxMessage(pmwatch.tempmax_in, "")
    if pmwatch.icontext == "test":
        settempmaxMessage(pmwatch.tempmax_out, "(max temp = 50° C)")


# quit the script when click on "Quit" in systray menu
def on_quit_callback(systray):
    systray.shutdown()
    sys.exit()


def reload_script(systray):
    print("reload")
    if pmwatch.icontext == "Out":
        os.startfile(
            r"PM sensor1.pyw") # modify this
        systray.shutdown()
        sleep(3)
        sys.exit()
    if pmwatch.icontext == "In":
        os.startfile(
            r"PM sensor1.pyw") # modify this
        systray.shutdown()
        sleep(3)
        sys.exit()

    if pmwatch.icontext == "test":
        print("\n\n\n\n")
        systray.shutdown()
        child = subprocess.Popen(
            ['python', r'\PMgeneral.pyw'], shell=True, stdout=subprocess.PIPE)  # modify this
        output, error = child.communicate()
        print(output, error)
        sys.exit()


def temp_too_high(icontext):

    # create message error
    script_name = os.path.basename(__file__)
    script_path = sys.argv[0]
    current_time = datetime.datetime.now().strftime(" %Y_%m_%d %Hh%Mm")
    if pmwatch.icontext == "Out":
        message_out = "(max=50°C)"
    else:
        message_out = ""

    html_for_file_and_email = fr"<b>Temp {icontext} PM sensor too high</b><br>It reached {pmwatch.temper}°C at {current_time} {message_out}<br><br> {script_path}"

    # create html file and open it in browser
    html_folder_path = r"C:\Users\<user>\Desktop\Scripts Admin\\"
    if not os.path.exists(html_folder_path):
        os.makedirs(html_folder_path)
    html_path = html_folder_path + script_name + \
        current_time + " temp too high.html"
    with open(html_path, "w") as text_file:
        text_file.write(html_for_file_and_email)
    # open html file in a new browser file
    new = 2
    webbrowser.open(html_path, new=new)

    # send email
    to = "some email @gmail.com" # modify this
    sender = "your email g@gmail.com" # modify this
    subject = f"Temp {icontext} PM sensor too high: it reached {pmwatch.temper}°C at {current_time} {message_out}"
    try:
        sendemail(sender, to, subject=subject,
                  message_text_html=html_for_file_and_email)
    except:
        pass


# main function
def pmwatch(url, voiceengine, iconcolorbackground, iconname, icontext, texttospeech):
    try:

        # custom VAR
        pmwatch.path_ahk_exe = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'  # ★
        pmwatch.path_ahk_script_unmute = r'unmute sound.ahk'  # ★
        pmwatch.path_ahk_script_countdown = r'countdown on mouse.ahk'  # ★
        pmwatch.texttospeech = texttospeech  # ★ start the script with sound on/off
        pmwatch.tempmax_out = 35  # ★
        pmwatch.tempmax_in = 27  # ★

        # other VAR
        # need to get value from the PM on the first check because we use a delay on the following check
        not_first_time = False

        # set working directory to the script folder
        os.chdir(sys.path[0])

        # var needed to be able to use the argument in the other defs (ex mute)
        pmwatch.icontext = icontext
        pmwatch.iconname = iconname
        pmwatch.iconcolorbackground = iconcolorbackground
        pmwatch.url = url
        pmwatch.connection_error = False
        pmwatch.connection_retry = 0

        # var needed to prevent bug when value from PM sensor haven't been yet retrieved
        pmwatch.pm25_rounded = 0
        pmwatch.pm10_rounded = 0
        pmwatch.temper = 0

        # end of VAR

        # ToastNotifier : not used, replaced by systray icon
        # script_name=os.path.basename(__file__)  # needed for ToastNotifier title
        # toaster = ToastNotifier()

        # start text reader engine with the choosen voiceengine
        try:
            engine = pyttsx3.init(driverName='sapi5')
            engine.setProperty('voice', voiceengine)
            engine.setProperty('rate', 100)
            engine.setProperty('volume', 1)
        except:
            pass

        # create icon in systray at start up - it makes it easier to use systray.update() later on
        create_image(icontext, "")
        systray_menu_settempmax = ("Set temp max", None, settempmax)
        systray_menu_reload = ("Reload", None, reload_script)

        pmwatch.menu_options_notexttospeech = (
            systray_menu_settempmax, systray_menu_reload,)  # ("Data", None, displaydata)
        pmwatch.menu_options_mute = (
            ("Mute", None, mute), systray_menu_settempmax, systray_menu_reload,)  # ("Data", None, displaydata)
        pmwatch.menu_options_unmute = (
            ("Unmute", None, unmute), systray_menu_settempmax, systray_menu_reload,)  # ("Data", None, displaydata)

        if pmwatch.texttospeech == "on":
            systray = SysTrayIcon(iconname, icontext, pmwatch.menu_options_unmute,
                                  on_quit=on_quit_callback)
        elif pmwatch.texttospeech == "off":
            systray = SysTrayIcon(iconname, icontext, pmwatch.menu_options_unmute,
                                  on_quit=on_quit_callback)
        else:  # pmwatch.texttospeech = disabled
            systray = SysTrayIcon(iconname, icontext, pmwatch.menu_options_notexttospeech,
                                  on_quit=on_quit_callback)
        systray.start()

        while True:
            # connect to sensor and retrieve the data as dico
            # retry 2 times after 5s, then 4 times after 15s, then 4 times after 30 s.
            for i in range(10):
                try:
                    response = requests.get(url)
                    pmwatch.connection_error = False
                except:
                    pmwatch.connection_retry = i + 1
                    pmwatch.connection_error = True
                    update_image_systray(systray)
                    if i < 2:
                        sleep(5)
                    elif i < 6:
                        sleep(15)
                    elif i < 9:
                        sleep(30)
                    else:
                        raise

            # previous way of doing it : pb = time increased between request + 0s, 1s, 2s, 4s, 8s, 16s, 32s, 64s (1m4s), 128s(2m8s), (4m16s), (8m32s), (17m4s)  + could add a way to signal that we are retrying...
            # s = requests.Session()
            # retries = Retry(total=15, backoff_factor=1, status_forcelist=[
            #                 500, 502, 503, 504])  # delay=3,
            # s.mount('http://', HTTPAdapter(max_retries=retries))
            # response = s.get(url)

            # if we resquest json too early (except for first connection), add some delay to wait for the new  PM value
            data = response.json()
            if float(data['age']) > 15 and not_first_time:
                time_to_wait = 146 - round(float(data['age']))
                if time_to_wait < 2:
                    time_to_wait = 2
                print(f"waiting time (delayed): {time_to_wait} s.")
                sleep(time_to_wait)  # Time in seconds

            # process the new value
            else:
                # save the needed values
                pm10 = data['sensordatavalues'][0]['value']
                pm25 = data['sensordatavalues'][1]['value']
                pmwatch.temper = data['sensordatavalues'][2]['value']
                humid = data['sensordatavalues'][3]['value']
                pmwatch.pm10_rounded = round(float(pm10))
                pmwatch.pm25_rounded = round(float(pm25))
                pmwatch.temper_rounded = round(float(pmwatch.temper))

                # print the new values
                print(
                    f"\t \t \t \t PM10: {pm10}   PM2.5: {pm25} Temp: {pmwatch.temper} Hum: {humid}", end="", flush=True)

                # speak the pm10 value only if sound is unmute
                try:
                    if pmwatch.texttospeech == "on":
                        speak(engine, pmwatch.pm10_rounded)
                except:
                    pass

                # add a line break  (we use no carriage for when printing value + in speak()  )
                print("")  # add the linebreak

                # create the icon for systray + update image
                update_image_systray(systray)

                # Create a warning if temperature too high : limit of SDS011 (sensor PM10) is 50°C
                if icontext == "In":
                    if pmwatch.temper_rounded > pmwatch.tempmax_in:
                        temp_too_high(icontext)
                        # round up tempmax_in to send next warning when 1°C higher
                        temper_float = float(pmwatch.temper)
                        pmwatch.tempmax_in = int(
                            temper_float) + ((int(temper_float) - temper_float) != 0)
                
                else:
                    if pmwatch.temper_rounded > pmwatch.tempmax_out:
                        temp_too_high(icontext)
                        # round up tempmax_out to send next warning when 1°C higher
                        temper_float = float(pmwatch.temper)
                        pmwatch.tempmax_out = int(
                            temper_float) + ((int(temper_float) - temper_float) != 0)  # this round up : the first int() round the var and if it was rounded down, ad 1



                # toaster.show_toast(script_name,
                #             f"Pm10 = {pm10}\nPm25 = {pm25}",
                #             icon_path=r".....",  #★
                #             duration=5)

                # after the first run, add the delay when we check to be sure we get a new value.
                not_first_time = True

                # time to wait before checking again for a new value
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
                    time_to_wait = time_to_wait - 1
                    print(time_to_wait, end="", flush=True)
                    sleep(1)
                print("")

                # display a count down next to the mouse (but disturbing because there is a delay when we move the mouse)
                # python will wait for the ahk script to finish before moving on.
                # if used, need to comment the  whole "while time_to_wait > 1"
                # subprocess.call([path_ahk_exe, path_ahk_script_countdown, str(time_to_wait)])

    # if the code fail, send an email with the error and other info and create an html and open it in webbrowser
    except Exception as e:
        pmwatch.connection_error = 2
        update_image_systray(systray)

        # create message error
        script_name = os.path.basename(__file__)
        script_path = sys.argv[0]
        error_type = str(e)
        traceback_error = traceback.format_exc()
        current_time = datetime.datetime.now().strftime(" %Y_%m_%d %H-%M-%S")
        html_for_file_and_email = fr'<b>Error in script {script_name}</b>:<br> {error_type}<br><br><b>Traceback:</b><br> {traceback_error}<br><br><b>Time of error:</b><br> {current_time}<br><br><b>Script path :</b><br> {script_path}'

        # create html file and open it in browser
        html_folder_path = r"C:\Users\<user>\Desktop\Scripts Admin\\"
        if not os.path.exists(html_folder_path):
            os.makedirs(html_folder_path)
        html_path = html_folder_path + script_name + current_time + " error.html"
        with open(html_path, "w") as text_file:
            text_file.write(html_for_file_and_email)
        # open html file in a new browser file
        new = 2
        webbrowser.open(html_path, new=new)

        # send email
        to = "some email@gmail.com" # modify this
        sender = "your email @gmail.com" # modify this
        subject = f"Error in script: {script_name}  ( xdtraceback ) "
        try:
            sendemail(sender, to, subject=subject,
                      message_text_html=html_for_file_and_email)
        except:
            pass


# # ●  needed to test (it works by running this script)
# if __name__ == "__main__":
#     # ##### Out
#     url = 'http://192.168.1.10/data.json'
#     # url = 'http://192.168.1.20/data.json'  #wrong ip to generate an error for testing
#     voiceengine = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0'
#     iconcolorbackground = (0, 255, 0)  # green for easy debug
#     iconname = 'pmout.ico'
#     icontext = 'test'
#     # options for texttospeech : disabled, off, on (but this requires autohotscript)
#     texttospeech = "on"

#     pmwatch(url, voiceengine, iconcolorbackground,
#             iconname, icontext, texttospeech)
