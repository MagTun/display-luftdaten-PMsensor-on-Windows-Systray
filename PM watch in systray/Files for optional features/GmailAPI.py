#  src
# https://medium.com/lyfepedia/sending-emails-with-gmail-api-and-python-49474e32c81f
# https://stackoverflow.com/a/41407166/3154274


# source  = https://developers.google.com/gmail/api/quickstart/python?authuser=2

# credential
from __future__ import print_function
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# send email
from apiclient import errors, discovery
from httplib2 import Http
from email.mime.text import MIMEText
import base64


# needed for attachment
import smtplib
import mimetypes
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
# List of all mimetype per extension: https://goo.gl/fq82pF  or http://mime.ritey.com/

# set working directory
import sys
import os


def create_message(emailFrom, emailTo, emailSubject, message_body, emailCc=None, html_content=None):
    try:
        message = MIMEMultipart('alternative')
        message['to'] = emailTo
        message['from'] = emailFrom
        message['subject'] = emailSubject
        message['Cc'] = emailCc
        body_mime = MIMEText(message_body, 'plain')
        message.attach(body_mime)
        if html_content:
            html_mime = MIMEText(html_content, 'html')
            message.attach(html_mime)
        return {
            'raw': base64.urlsafe_b64encode(
                bytes(
                    message.as_string(),
                    "utf-8")).decode("utf-8")}
    except Exception as e:
        print('Error in CreateMessage()', e)
        return '400'


def create_Message_with_attachment(sender, to, subject, message_text_plain, message_text_html=None, file=None, message_cc=None, message_bcc=None):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

    Returns:
    An object containing a base64url encoded email object.
    """

    # An email is composed of 3 part :
    # part 1: create the structure of the message using a dictionary containing { to, from, subject }
    # part 2: attach the message_text with .attach()
    # part 3(optional): an attachment added with .attach()

    # Part 1
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['Cc'] = message_cc
    message['Bcc'] = message_bcc

    # Part 2	(the message_text)
    message.attach(MIMEText(message_text_html, 'html'))
    message.attach(MIMEText(message_text_plain, 'plain'))

    # Part 3 (attachement)

    # -----About MimeTypes:
    # It tells gmail which application it should use to read the attachement (it acts like an extension for windows). If you dont provide it, you wont be able to read the attachement (eg. a text) within gmail. You'll have to download it to read it (windows will know how to read it with it's extension).

    # -----3.1 get MimeType of attachment
    # option 1: if you know the file you want to send, just specify it’s mime types

    # option 2: use mimetypes.guess_type(file)(let's say it's a .mp3)
    if file != None and file != "":
        my_mimetype, encoding = mimetypes.guess_type(file)
        print(my_mimetype, encoding)
        # on unknown extension, return (None, None)

        # return (audio/mp3, None)

        if my_mimetype is None or encoding is not None:
            # for unrecognized extension, set my_mimetype to  'application/octet-stream', so it won't return None again.
            my_mimetype = 'application/octet-stream'

        # if my_mimetype is audio/mp3, main_type = audio and sub_type = mp3
        main_type, sub_type = my_mimetype.split(
            '/', 1)  # split only at the first '/'

        # print(main_type, sub_type) #● debug

        # -----3.2  creating the attachement
        # you don't really "attach" the file but you attach a variable that contains the "binary content" of the file you want to attach (let's call this variable attachement)
        # option 1: use MIMEBase for all my_mimetype (cf below)  - this is the easiest one to understand
        # option 2: use the specific MIME (ex for .mp3 = MIMEAudio)   - it's a shorcut version of MIMEBase

        if main_type == 'text':
            print("text")
            # do not use 'rb', it give error : 'bytes' object has no attribute 'encode'
            temp = open(file, 'r')
            attachement = MIMEText(temp.read(), _subtype=sub_type)
            temp.close()

        elif main_type == 'image':
            print("image")
            temp = open(file, 'rb')
            attachement = MIMEImage(temp.read(), _subtype=sub_type)
            temp.close()

        elif main_type == 'audio':

            if sub_type == "m4a":
                print("in if: audio m4a")
                temp = open(file, 'rb')
                attachement = MIMEAudio(temp.read(), _subtype='x-m4a')
                temp.close()

            else:  # sub_type == "mp3":
                print("in if: audio mp3")
                temp = open(file, 'rb')
                attachement = MIMEAudio(temp.read(), _subtype=sub_type)
                temp.close()
        elif main_type == 'application' and sub_type == 'pdf':
            temp = open(file, 'rb')
            attachement = MIMEApplication(temp.read(), _subtype=sub_type)
            temp.close()

        else:
            print("else")
            attachement = MIMEBase(main_type, sub_type)
            temp = open(file, 'rb')
            attachement.set_payload(temp.read())
            temp.close()

        # -----3.3 encode the attachment, add a header and attach it to the message
        # https://docs.python.org/3/library/email-examples.html
        encoders.encode_base64(attachement)
        filename = os.path.basename(file)
        # name preview in email
        attachement.add_header('Content-Disposition',
                               'attachment', filename=filename)
        message.attach(attachement)

    # Part 4 encode the message (the message should be in bytes
    # the message should converted from string in bytes...
    message_as_bytes = message.as_bytes()
    message_as_base64 = base64.urlsafe_b64encode(message_as_bytes)
    raw = message_as_base64.decode()  # need to JSON serializable
    return {'raw': raw}


def send_message(service, user_id, message):
    """Send an email message.
    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.
    Returns:
      Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())

        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def service_account_login():

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    script_name = os.path.basename(__file__)
    path_to_token_pickle = fr"C:\Users\<user>\.credentials\{script_name}.pickle"
    creds = None
    if os.path.exists(path_to_token_pickle):
        with open(path_to_token_pickle, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open(path_to_token_pickle, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def sendemail(sender, to, subject="", message_text_plain="", message_text_html="", file="", message_cc="", message_bcc=""):
    service = service_account_login()
    message1 = create_Message_with_attachment(
        sender, to, subject, message_text_plain, message_text_html, file, message_cc, message_bcc)

    sent = send_message(service, 'me', message1)


def main():

    # ============================================================== ¤ send email with
    os.chdir(sys.path[0])
    to = "some email@gmail.com"  # modify this
    sender = "some email @gmail.com"  # modify this
    subject = "From def main"
    # Some users can only see plain text so it may be usefull to join plain + html
    message_text_html = r'Hi<br/>This is an Html <b>email</b> <font color="red">Great!</font><p></p>'
    message_text_plain = "Hi, message with only text,\n not html"
    file = ""
    message_cc = ""  # modify this  if needed
    message_bcc = ""  # modify this  if needed
    service = service_account_login()

    message1 = create_Message_with_attachment(
        sender, to, subject, message_text_plain, message_text_html, file, message_cc, message_bcc)

    sent = send_message(service, 'me', message1)


if __name__ == "__main__":
    main()
