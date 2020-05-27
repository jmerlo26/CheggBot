from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import *
import googleapiclient

import email

import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import email.encoders
import os

from apiclient import errors

import cheggSelenium
import os

def GetMessage( service: object, user_id: object, msg_id: object ) -> object:
    """Get a Message with given ID.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Returns:
      A Message.
    """
    try:
        message = service.users().messages().get( userId = user_id, id = msg_id, format = 'full' ).execute()

        sentFrom = ''

        for d in message['payload']['headers']:
            if d['name'] == 'From':
                sentFrom = d['value']

        text = None
        
        try:
            x = message['payload']['parts']
        except:
            return sentFrom, text

        for part in message['payload']['parts']:
            try:
                body = (base64.urlsafe_b64decode( part['body']['data'].encode( "ASCII" ) ).decode( "utf-8" ))
                if body.startswith( "'https:" ) or body.startswith('https:'):
                    text = body
            except:
                pass

        return sentFrom, text
    except errors.HttpError as error:
        print( 'An error occurred: %s' % error )


def GetMessages( service, user_id, msg_id ):
    """Get a Message with given ID.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

    Returns:
    A Message.
    """
    try:
        response = service.users().messages().list( userId = user_id ).execute()

        messages = []
        if 'messages' in response:
            messages.extend( response['messages'] )

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list( userId = user_id, pageToken = page_token ).execute()
            messages.extend( response['messages'] )

        return messages
    except errors.HttpError as error:
        print( 'An error occurred: %s' % error )


def GetMimeMessage( service, user_id, msg_id ):
    """Get a Message and use it to create a MIME Message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

     Returns:
    A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get( userId = user_id, id = msg_id,
                                                  format = 'raw' ).execute()

        print( 'Message snippet: %s' % message['snippet'] )

        msg_str = base64.urlsafe_b64decode( message['raw'].encode( 'ASCII' ) )

        mime_msg = email.message_from_string( msg_str )

        return mime_msg
    except errors.HttpError as error:
        print( 'An error occurred: %s' % error )


def CreateMessageWithAttachment(sender, to, subject, message_text, file_dir,filename):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file_dir: The directory containing the file to be attached.
      filename: The name of the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText( message_text )
    message.attach( msg )

    path = os.path.join( file_dir, filename )
    print(path)
    content_type, encoding = mimetypes.guess_type( path )

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split( '/', 1 )
    if main_type == 'text':
        fp = open( path, 'rb' )
        msg = MIMEText( fp.read(), _subtype=sub_type )
        fp.close()
    elif main_type == 'image':
        fp = open( path, 'rb' )
        msg = MIMEImage( fp.read(), _subtype=sub_type )
        fp.close()
    elif main_type == 'audio':
        fp = open( path, 'rb' )
        msg = MIMEAudio( fp.read(), _subtype=sub_type )
        fp.close()
    else:
        fp = open( path, 'rb' )
        msg = MIMEBase( main_type, sub_type )
        msg.set_payload( fp.read() )
        fp.close()


    msg.add_header( 'Content-Disposition', 'attachment', filename = filename )
    email.encoders.encode_base64(msg)
    message.attach( msg )
    #message.attach( msg )

    return {'raw': base64.urlsafe_b64encode( message.as_string().encode('UTF-8')).decode('ascii') }


def SendMessage(service, user_id, message):
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
        message = (service.users().messages().send( userId = user_id, body = message ).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def reply( sender, text, driver, service ):
    text = text.replace( "'", "" )
    startindex = sender.find( "<" )
    endindex = sender.find( ">" )
    email = sender[startindex + 1:endindex]
    print( email )

    nameindex = email.find( '@' )
    name = email[:nameindex]
    print( name )
    driver.get( text )
    time.sleep( 7 )
    cheggSelenium.toPDF( driver, name )

    #send email
    sender = ''#Your Email here!
    subject = 'Your Chegg Answer'
    outText = ''
    fileDir = 'Chegg/output'
    replyEmail = CreateMessageWithAttachment(sender=sender, to=email, subject=subject,message_text = outText, file_dir = fileDir,filename = f'{name}.pdf')

    SendMessage(service, 'me', replyEmail)
    #delete pdf
    os.remove(f'./output/{name}.pdf')

    #get off chegg
    time.sleep(15)
    driver.get("http://www.google.com")



# todo add log
def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    driver = cheggSelenium.setup()

    creds = None

    if os.path.exists( 'token.pickle' ):
        with open( 'token.pickle', 'rb' ) as token:
            creds = pickle.load( token )
    # If there are no (valid) credentials available, let the user log in.


    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh( Request() )
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES )
            creds = flow.run_local_server( port = 0 )
        # Save the credentials for the next run
        with open( 'token.pickle', 'wb' ) as token:
            pickle.dump( creds, token )

    service = build( 'gmail', 'v1', credentials = creds )

    # Call the Gmail API
    results = service.users().labels().list( userId = 'me' ).execute()
    labels = results.get( 'labels', [] )
    print('sleeping')
    #time.sleep(100)
    if not labels:
        print( 'No labels found.' )
    else:
        print( 'Labels:' )
        for label in labels:
            print( label )
    driver.get('https://www.google.com')
    time.sleep(5)
    #Loop to watch for incoming mail and respond
    while True:
        messages = GetMessages( service, 'me', '' )
        try:
            for message in messages:
                sender, text = GetMessage( service, 'me', message['id'] )
                if text:
                    reply( sender, text, driver, service )
                    service.users().messages().trash(userId = 'me', id=message['id']).execute()
                    time.sleep(3)
            time.sleep(5)
        except:
            print('Cannot Iterate Messages!')

if __name__ == '__main__':
    main()

'''
https://www.chegg.com/homework-help/find-mass-jupiter-based-data-orbit-one-moons-compare-result-chapter-6-problem-45pe-solution-9781938168000-exc
https://www.chegg.com/homework-help/questions-and-answers/astronomy-light-year-ly-d-ned-distance-light-would-travel-one-year-many-meters-ly-q2809870
https://www.chegg.com/homework-help/astronomers-use-light-year-measure-distance-lightyear-distan-chapter-14.1-problem-23b-solution-9780321987297-exc
'''