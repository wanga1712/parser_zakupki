from ftplib import FTP

ftp = FTP('ftp://zakupki.gov.ru')
ftp.login('free')
data = ftp.retrlines('LIST')

print(data)