# Luftdaten stuff


## All data on a webpage/PM values.html
This html script access all the data of two luftdaten PM sensors (Indoor and Outdoor), scraped from the local address http://192.168.1.xx/values and from the Madawi website. 

<img src="All%20data%20on%20a%20webpage/All%20data%20from%202%20PM%20sensors%20side%20by%20side.png" width="100" height="200">


## PM watch in systray
This python app displays the PM value of a luftdaten PM sensor in the systray (it works on Windows 10 but can be adapted to other OS).  
You can have several icons displaying the data from several sensors but duplicating the `PM sensor1.py` script. 

![PM watch](https://user-images.githubusercontent.com/15843700/63337986-438bbd00-c342-11e9-87ca-49c70884948f.png)


### Installing of the dependencies : 
The app needs Python 3  (open source): download and install the latest Python 3 (e.g.: https://www.python.org/downloads/release/python-374/)

The app also needs these 3 libraries:
- Pillow (to create/update the icon displayed in the systray )
- sys.tray (to display the icon created by Pillow in the systray)
- easygui (the little message needed to set the max temperature before the script generates alerts)

To install them, open a Command windows and copy each line below and press enter:
`python -m pip install Pillow`  
`python -m pip easygui`  

We use a modified version of the library sys.tray: 
- You need to install the “regular” version of sys.tray with : `python -m install infi.systray`  
- During the installation go to this [link](https://github.com/MagTun/infi.systray/blob/develop/src/infi/systray/traybar.py) and copy the content of the file.   
- Once the installation is finished, go to your Python installation folder (probably C:\Users\<username>\AppData\Local\Programs\Python\Python37) and navigate to the folder `Lib\site-packages\infi\systray`  
- Open the file `traybar.py` and replace all its content by the one you just copied.   


The app has some optional features that require other libraries:  
- text to speech (it read aloud the PM value): this feature is easy to enable  
- send emails when the temperature is too high or if the script bugs: it’s more difficult to enable this feature but doable if you have just a little programming knowledge    



### Installing the script
####  If you do not want any optional features: 
- Download the 2 files in [this folder](https://github.com/MagTun/luftdaten-stuff/tree/master/PM%20watch%20in%20systray/Main%20app): 
- Right-click the file `PM sensor1.pyw` and select Edit.   
- Modify the `url` so that it matches your sensor url (ex: http://192.168.1.10/data.json).   
- You can also change the color of the icon (you need to change the rgb color code for `iconcolorbackground` : https://www.w3schools.com/colors/colors_picker.asp).   
- Ignore all the other parameters.  
- Save your file then double-click on `PM sensor1.pyw`.  
After 3-5 seconds, you should see the icon with the PM displayed in you systray.  

#### If you want all the features (text to speech and alert emails): 
- Install the required dependencies
   - For text to speech : you need to install `pyttsx3` (in a Command: python -m pip pyttsx3) and Autohotkey (an open source programming language used it to unmute the sound of the computer when text to speech is enable - couldn’t find a way to do this with python3).   
  
   - For emails alert:  
      - The script uses the GMAIL API so you need a Gmail account. You also need to install the gmail API follow this tuto: https://developers.google.com/gmail/api/quickstart/python?authuser=2 (if you have multiple active Gmail account, replace the 2 at the end of the url by the corresponding Gmail account number you want to use to send the alerts).  
      - With this tuto, you will download the required libraries for the Gmail API, enable a Google developer account (it’s free), enable the Gmail API on your Google developer account and download the required credentials so you script won’t be blocked by Gmail when it sends an email with your Gmail account.  

- Download all the files in [this folder](https://github.com/MagTun/luftdaten-stuff/tree/master/PM%20watch%20in%20systray/Main%20app) and [this folder](https://github.com/MagTun/luftdaten-stuff/tree/master/PM%20watch%20in%20systray/Files%20for%20optional%20features)  
   - In `GmailAPI.py`, modify the `path_to_token_pickle` in `service_account_login()`
   - In `PMgeneral.pyw`, modify:  
        -  the path to import for `GmailAPI`  
        - the `to` and `sender` in temp_too_high()   
   - In `PM sensor1.pyw`, modify the url, the voiceengine and the texttospeech value  












