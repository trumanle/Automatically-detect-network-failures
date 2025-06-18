import time
from ping3 import ping, verbose_ping
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# 配置
devices = [
    {"name": "Router1", "ip": "192.168.1.1"},
    {"name": "Switch1", "ip": "192.168.1.2"},
    # 可添加更多设备
]

PING_COUNT = 5
PING_INTERVAL = 60  # 检查间隔（秒）
LOSS_THRESHOLD = 0.2  # 丢包率阈值（20%）
DELAY_THRESHOLD = 100  # 平均延迟阈值（毫秒）

# 邮件通知配置
MAIL_HOST = "smtp.example.com"
MAIL_PORT = 587
MAIL_USER = "your_email@example.com"
MAIL_PASS = "your_password"
MAIL_TO = "notify_to@example.com"

def send_email(subject, content):
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = MAIL_USER
    msg["To"] = MAIL_TO

    try:
        server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(MAIL_USER, [MAIL_TO], msg.as_string())
        server.quit()
        print("通知邮件已发送。")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def check_device(device):
    ip = device["ip"]
    name = device["name"]
    success = 0
    delays = []

    for _ in range(PING_COUNT):
        delay = ping(ip, timeout=2)
        if delay is not None:
            success += 1
            delays.append(delay * 1000)  # 转为毫秒
        time.sleep(1)

    loss_rate = 1 - (success / PING_COUNT)
    avg_delay = sum(delays) / len(delays) if delays else None

    return loss_rate, avg_delay

def main():
    while True:
        for device in devices:
            loss, delay = check_device(device)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] {device['name']}({device['ip']}): 丢包率={loss*100:.1f}%, 平均延迟={delay:.1f}ms" if delay else "无响应")

            if loss > LOSS_THRESHOLD or (delay is not None and delay > DELAY_THRESHOLD):
                subject = f"网络设备异常告警: {device['name']}({device['ip']})"
                content = f"""检测时间: {now}
设备: {device['name']} ({device['ip']})
丢包率: {loss*100:.1f}%
平均延迟: {delay:.1f}ms
请及时检查设备状态！
"""
                send_email(subject, content)
            elif delay is None:
                subject = f"网络设备离线告警: {device['name']}({device['ip']})"
                content = f"""检测时间: {now}
设备: {device['name']} ({device['ip']})
状态: 无响应（可能离线）
请及时检查设备状态！
"""
                send_email(subject, content)
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()