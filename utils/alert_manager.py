import smtplib
from email.mime.text import MIMEText

class AlertManager:
    def __init__(self, email_config=None):
        self.email_config = email_config

    def send_email_alert(self, subject, body):
        if not self.email_config:
            print("Configuração de e-mail não fornecida. Alerta por e-mail não enviado.")
            return

        sender_email = self.email_config.get("sender_email")
        sender_password = self.email_config.get("sender_password")
        receiver_email = self.email_config.get("receiver_email")
        smtp_server = self.email_config.get("smtp_server")
        smtp_port = self.email_config.get("smtp_port")

        if not all([sender_email, sender_password, receiver_email, smtp_server, smtp_port]):
            print("Configuração de e-mail incompleta. Alerta por e-mail não enviado.")
            return

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
            print(f"Alerta por e-mail enviado para {receiver_email}")
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

    def send_telegram_alert(self, message):
        # Implementação futura para Telegram
        print(f"Alerta por Telegram (não implementado): {message}")


