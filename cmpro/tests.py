



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 第三方 SMTP 服务
mail_host = "smtp.qq.com"  # 设置服务器
mail_user = "2712060002@qq.com"  # 用户名
mail_pass = "orpvsvddzdykdgdh"  # 口令

sender = '2712060002@qq.com'  # 发送方
receivers = ['512774625@qq.com', ]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱 可写多个

# 创建一个带附件的实例
message = MIMEMultipart()
message['From'] = Header("Django-CM系统", 'utf-8')  # 发件人
message['To'] = Header("开发者", 'utf-8')   # 收件人

subject = '商品数据库备份'    #邮件主题
message['Subject'] = Header(subject, 'utf-8')

# 邮件正文内容
send_content = '最新的商品库存管理数据库备份文件'
content_obj = MIMEText(send_content, 'plain', 'utf-8')  # 第一个参数为邮件内容
message.attach(content_obj)

# 构造附件1，发送当前目录下的 t1.txt 文件
att1 = MIMEText(open(r'D:\test.txt', 'rb').read(), 'base64', 'utf-8')
att1["Content-Type"] = 'application/octet-stream'
# 这里的filename可以任意写，写什么名字，邮件附件中显示什么名字
att1["Content-Disposition"] = 'attachment; filename="test.txt"'
message.attach(att1)

try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())

except smtplib.SMTPException:
    pass