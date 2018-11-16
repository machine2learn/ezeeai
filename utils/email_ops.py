import smtplib

smtpserver = 'smtp.gmail.com:587'


def send_email(user_info, server_info):
    body = 'Your model has finished training.\n\n Machine2Learn'
    to = user_info['email_address']
    sfrom = server_info['email_address']
    subject = "Training finished"

    msg = "\r\n".join([
        "From: %s" % sfrom,
        "To: %s" % to,
        "Subject: %s" % subject,
        "",
        "%s" % body
    ])


    server = smtplib.SMTP(smtpserver)
    server.ehlo()
    server.starttls()
    server.login(server_info['login'], server_info['password'])
    server.sendmail(server_info['email_address'], user_info['email_address'], msg)
    server.quit()