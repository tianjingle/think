import smtplib
import time
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


class SendEmail:

    def sendStockInfo(self,codes):
        imgsOKstr = "当下可选股票："
        for item in codes:
            imgsOKstr = imgsOKstr + "<p>" + str(item[0]) + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(item[1])+"<img src='cid:"+item[0]+"'></p>"
        endDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        my_pass = 'tmugmrbimrcddead'  # 发件人邮箱密码
        my_user = '2695062879@qq.com'  # 收件人邮箱账号，我这边发送给自己
        sender = '2695062879@qq.com'
        receivers = ['2695062879@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = Header(str(endDate) + " 大盘趋势", 'utf-8')
        msgRoot['To'] = Header("测试", 'utf-8')
        subject = str(endDate) + ' 趋势'
        msgRoot['Subject'] = Header(subject, 'utf-8')

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        mail_msg = imgsOKstr
        msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))

        # 指定图片为当前目录
        for item in codes:
            fp = open('E:\\' + item[0] + ".png", 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            temp = "<" + item[0] + ">"
            # 定义图片 ID，在 HTML 文本中引用
            msgImage.add_header('Content-ID', temp)
            msgRoot.attach(msgImage)

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect('smtp.qq.com', 25)  # 25 为 SMTP 端口号
            smtpObj.login(my_user, my_pass)
            smtpObj.sendmail(sender, receivers, msgRoot.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
    # os.system('shutdown -s -f -t 180')