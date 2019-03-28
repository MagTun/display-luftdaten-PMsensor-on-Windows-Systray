import PMgeneral
url = 'http://192.168.1.15/data.json'
voiceengine= 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
iconcolorbackground  = (242, 142, 238)
iconname='pmint.ico'
icontext='Int'

PMgeneral.pmwatch(url, voiceengine, iconcolorbackground, iconname, icontext)
