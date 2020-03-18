"""
用于对mysql数据库进行备份（已在linux环境中测试没问题）
"""
import os
import time
import smtplib
from django.conf import settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


class AutoDumpMysqlData:
        HOST = settings.DATABASES['default']['HOST']
        PORT = settings.DATABASES['default']['PORT']
        USER = settings.DATABASES['default']['USER']
        PASSWORD = settings.DATABASES['default']['PASSWORD']
        DB = settings.DATABASES['default']['NAME']
        TABLE = 'cmpro_commodity'
        CHARSET = 'utf8'
        INTERVAL = settings.DB_DUMP_INTERVAL               # 间隔时间，目前设定是一周
        LINUX_FILE_DIR = '/usr/datadump'       # linux下文件路径

        def get_file_name(self):
            """
            生成自动备份的文件名（以时间戳来作为文件名，以便根据时间戳判断来进行自动化备份）
            """
            now = time.time()
            linux_file_name = "{pwd}/{now}.sql".format(pwd=self.LINUX_FILE_DIR,now=now)           # 这里留着部署服务器时候用
            return linux_file_name

        def get_SQL(self):
            """
            生成备份数据库的SQL语句：mysqldump -u 用户名 -p -d 数据库名 -t 表名 > 盘符:\路径\文件名.sql
            mysqldump -uroot -pquegai18 -d cmprotest -t cmpro_commodity > /usr/datadump/1584083307.88076.sql
            """
            fileName = self.get_file_name()
            sql = 'mysqldump -u{user} -p{password} -d {db_name} -t {table_name} > {file_name}'.format(
                user=self.USER,
                password=self.PASSWORD,
                db_name=self.DB,
                table_name=self.TABLE,
                file_name=fileName
            )
            return sql

        def send_email(self):
            """用于发送数据库备份文件"""
            file_name = os.listdir(self.LINUX_FILE_DIR)[0]
            path = "{pwd}/{file}".format(pwd=self.LINUX_FILE_DIR, file=file_name)
            # 第三方 SMTP 服务
            mail_host = settings.EMAIL_HOST  # 设置服务器
            mail_user = settings.EMAIL_HOST_USER  # 用户名
            mail_pass = settings.EMAIL_HOST_PASSWORD  # 口令
            sender = settings.EMAIL_HOST_USER  # 发送方
            receivers = ['512774625@qq.com', ]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱 可写多个
            # 创建一个带附件的实例
            message = MIMEMultipart()
            message['From'] = Header("Django-CM系统", 'utf-8')  # 发件人
            message['To'] = Header("开发者", 'utf-8')  # 收件人
            subject = '商品数据库备份'  # 邮件主题
            message['Subject'] = Header(subject, 'utf-8')
            # 邮件正文内容
            send_content = '最新的商品库存管理数据库备份文件'
            content_obj = MIMEText(send_content, 'plain', 'utf-8')  # 第一个参数为邮件内容
            message.attach(content_obj)
            # 构造附件1，发送当前目录下的 t1.txt 文件
            att1 = MIMEText(open(path, 'rb').read(), 'base64', 'utf-8')
            att1["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件附件中显示什么名字
            att1["Content-Disposition"] = 'attachment; filename="backend.sql"'
            message.attach(att1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
                smtpObj.login(mail_user, mail_pass)
                smtpObj.sendmail(sender, receivers, message.as_string())
            except smtplib.SMTPException:
                pass

        def implement_SQL(self):
            """
            用于执行上面的备份指令
            :return:
            """
            cmd = self.get_SQL()  # 获取要执行的SQL命令
            os.system(cmd)        # 开始执行
            self.send_email()     # 发送备份文件到我的邮箱

        def check_file(self):
            """
            校验功能：查看时间间隔，我这里暂时设定为一周，如果超过一周了，就进行备份，如果没有，那就算了
            """
            file_list = os.listdir(self.LINUX_FILE_DIR)       # 获取文件路径
            if len(file_list) == 0:      # 这里进行第一次备份
                self.implement_SQL()
            else:
                # ['1584086604.2046597.sql']

                last_time = int(file_list[0].split('.',1)[0])        # 这是之前存档的时间
                now_time = int(time.time())                          # 这是当前时间
                time_difference = now_time - last_time               # 时间差
                if time_difference > self.INTERVAL:
                    file_path = "{pwd}/{file_name}".format(pwd=self.LINUX_FILE_DIR, file_name=file_list[0])
                    os.remove(file_path)       # 删除原路径下的文件
                    self.implement_SQL()       # 生成新的文件


