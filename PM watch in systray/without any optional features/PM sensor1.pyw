import PMgeneral
url = 'http://192.168.1.15/data.json'
iconcolorbackground = (242, 142, 238)  # to change the color background of your icon, chnage this rgb code
iconname = 'pmin.ico'
icontext = 'In'
voiceengine = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
# options for texttospeech : disabled, off, on (but this requires autohotscript)
texttospeech = "disabled"

PMgeneral.pmwatch(url, voiceengine, iconcolorbackground,
                  iconname, icontext, texttospeech)
