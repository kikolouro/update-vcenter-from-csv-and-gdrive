from datetime import date
import smtplib
from os.path import basename
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
from email.utils import formataddr
import os
import sys
import json
from decouple import config
import pprint

pp = pprint.PrettyPrinter(indent=4)


def render_template(template, **kwargs):
    ''' renders a Jinja template into HTML '''
    # check if template exists
    # print(os.path.exists(template))
    if not os.path.exists(template):
        print('No template file present: %s' % template)
        sys.exit()

    import jinja2
    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template(template)
    # print(templ.render(**kwargs))
    return templ.render(**kwargs)


def sendEmail(receiver, senderdata, data, port=465, smtpserver='smtp.gmail.com'):
    sender_email = senderdata['email']
    password = senderdata['password']
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['Subject'] = "Vcenter Update - " + data['datetime']
    html = render_template(f'{os.getcwd()}/template.j2', data=data)
    msg.attach(MIMEText(html, 'html'))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
        server.login(sender_email, password)
        msg['To'] = ''.join(receiver)
        server.sendmail(sender_email, receiver, msg.as_string())

    return True

def sendEmailwithAttachment(receiver, senderdata, filename, warnings, port=465, smtpserver='smtp.gmail.com'):
    sender_email = senderdata['email']
    password = senderdata['password']
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email

    msg['Subject'] = f"Vcenter Export - {str(date.today())} [{len(warnings)} Warnings]" 
    mail_content = f"Vcenter Export - {date.today()}\n\n"
    

    for warning in warnings:
        mail_content += f"{warning}\n"

    msg.attach(MIMEText(mail_content, 'plain'))
    with open(filename, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())
        
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    msg.attach(part)
    context = ssl.create_default_context()


    with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
        server.login(sender_email, password)
        msg['To'] = ''.join(receiver)
        server.sendmail(sender_email, receiver, msg.as_string())

    return True