from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import os
from os import environ
from datetime import timedelta
import getpass, imaplib
import sys
import string


class ExtractAttachment(BaseOperator):
    """
    Extract data from Gmail into GCS
    """ 

    @apply_defaults
    def __init__(   # Defining the Gmail inbox name where the data resides
            self,
            inbox_name,
            *args, **kwargs):

        super(ExtractAttachment, self).__init__(*args, **kwargs)
        self.inbox_name = inbox_name
        self.file_path = 'filepath_to_save_CSV'

    def __extract_email_attachment(self, execution_date): # 

        userName = 'your username' # Setting our Gmail Username and Password ( Yes, unfortunately it will be visible to whoever views the code )
        passwd = 'your password' 

        
        imapSession = imaplib.IMAP4_SSL('imap.gmail.com')   # Setting up an IMAP session, logging in with the credentials
        typ, accountDetails = imapSession.login(userName, passwd)
        if typ != 'OK':
            print('Not able to sign in!')

            
        imapSession.select(self.inbox_name) # Searching for the Gmail label inbox named as the inbox_name parameter
        typ, data = imapSession.search(None, 'Unseen') # Selecting only the emails which are Unseen only, this is important as we do not want to load the same data twice
        if typ != 'OK':
            print('Error searching Inbox.')

        
        # Iterating over all emails
        for msgId in data[0].split():
            typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
            if typ != 'OK':
                print('Error fetching mail.')

            
            raw_email = messageParts[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    # print part.as_string()
                    continue
                if part.get('Content-Disposition') is None:
                    # print part.as_string() 
                    continue
                fileName = part.get_filename()

                if bool(fileName):
                    filePath = self.file_path + fileName
                    print(filePath)
                    if not os.path.isfile(filePath) :
                        print(fileName)
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
            imapSession.uid('STORE',msgId, '+FLAGS', '\SEEN') 
        imapSession.close()
        imapSession.logout()
        
    def execute(self, context):
        self.__extract_email_attachment(execution_date)
        
# checking if there are any files to be loaded into Google Bigquery using the ShortCircuit Operator. If there isn’t a file to be loaded, all downstream tasks of this operator are skipped, and the DAG is successfully completed
        
        
    
        
        
        
        
        