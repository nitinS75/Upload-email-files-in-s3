import boto3
import email
import config
import imaplib


s3_client = boto3.client(
    's3',
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.region_name
)

class EmailFileExport(): 
    
    def __init__(self, search_type=config.SEARCH_TYPE, search_value=config.SEARCH_VALUE):      
        self.search_type = search_type
        self.search_value = search_value
        
        self.mails_detail = {}
        self.mail_send_by = []
    
    def read_email_files(self):
        mail = imaplib.IMAP4_SSL(config.MAIL_READ_HOST, config.MAIL_READ_PORT)
        mail.login(config.EMAIL_ID, config.APP_PASSWORD)
        mail.select('Inbox')
 
        type, data = mail.search(None,f'({self.search_type} "{self.search_value}")')

        mails = data[0].split()
        
        for em in mails[::-1]:
            type,fetched_mail  = mail.fetch(em, '(RFC822)')
            bytes_data = fetched_mail[0][1]
            email_string = bytes_data.decode('utf-8')
            email_message = email.message_from_string(email_string)
            
            for part in email_message.walk():
                mail_details = str(email_message).split("\n")

                for field in mail_details:
                    
                    if "Date: " in field:
                        mail_date= str(field.split(":",1)[1].replace("-","+").split("+")[0].split(",")[1][1:-1]).replace("GM",'')
                    
                    elif "To: " in field:
                        if "@" in field:
                            self.mail_receiver = field.split(" ")[-1].replace("<","").replace(">","")

                    elif "Message-ID:" in field:
                        self.message_id = email_message['Message-ID'].strip().replace(' ','').replace('\r\n', '')

                    elif "From: " in field:
                        if "@" in field:
                            self.mail_sender = field.split(" ")[-1].replace("<","").replace(">","")
                                            
                self.file_actual_name = str(part.get_filename()) # getting attached file name 
                
                if self.file_actual_name[-4:].lower()==".png":
                    continue
                
                if self.file_actual_name[-4:].lower()==".csv":
                    self.mail_send_by.append(self.mail_sender)
                    self.mails_detail[self.file_actual_name] = part.get_payload(decode=True)
        return  f'Total files  :- {len(self.mail_send_by)}'
                                            
    def file_upload_to_s3(self):
        
        for (key, value), sender_mail in zip(self.mails_detail.items(), self.mail_send_by):
            print("\n\tmail_receiver: ", self.mail_receiver)
            print("\n\tmail_sender: ",sender_mail)
            print("\n\tfile_name: ",key)
            s3_client.put_object(Body=value, Bucket = config.BUCKET_NAME, Key=f'{config.KEY}/{key}')        
        
        return {'status': 200, 'message': 'All files has been uploaded!!'}
    

