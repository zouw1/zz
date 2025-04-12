import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SMTP配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # 改回465端口
SMTP_USER = "1111111@qq.com"
SMTP_PASSWORD = "tpriwckpneusebje"

async def send_reset_email(to_email: str, reset_token: str):
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = "密码重置请求"
        
        # 修改链接显示方式
        body = f"""
        <html>
            <body>
                <h2>密码重置请求</h2>
                <p>您收到这封邮件是因为您请求重置密码。</p>
                <p>请复制下面的链接到浏览器打开（30分钟内有效）：</p>
                <p style="background-color: #f5f5f5; padding: 10px; word-break: break-all;">
                    http://127.0.0.1:8000/reset-password.html?token={reset_token}
                </p>
                <p>如果您没有请求重置密码，请忽略此邮件。</p>
                <p style="color: #666; font-size: 12px;">
                    注意：如果链接无法打开，请确保您的应用服务器正在运行。
                </p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        logger.info("正在连接SMTP服务器...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)
        
        logger.info("正在登录...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        logger.info("登录成功")
        
        logger.info(f"正在发送邮件到 {to_email}")
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        logger.info("邮件发送成功")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP认证失败：可能是授权码错误")
        logger.error(str(e))
        return False
    except smtplib.SMTPException as e:
        logger.error("SMTP错误：")
        logger.error(str(e))
        return False
    except Exception as e:
        logger.error("发送邮件时出现错误：")
        logger.error(traceback.format_exc())
        return False 