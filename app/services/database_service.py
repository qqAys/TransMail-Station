import json

import pymysql

from app.models.email_model import Email, MailStatus
from app.utils.util import Config, logger, app_name

CANCEL = MailStatus.CANCEL.value
PENDING = MailStatus.PENDING.value


class DatabaseService:
    def __init__(self):
        config = Config()
        db_config = config.app_database
        self.db_name = app_name.lower().replace("-", "_")
        try:
            self.db = pymysql.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
            )
            logger.info("Database connection successful.")
        except pymysql.err.OperationalError:
            massage = "Database connection failed."
            logger.error(massage)
            raise RuntimeError(massage)
        self.db_init()

    def db_init(self):
        # 建库
        with self.db.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            if self.db_name not in [_db[0].lower() for _db in cursor.fetchall()]:
                logger.info(f"Database {self.db_name} does not exist, creating...")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.db_name}`;")
                self.db.commit()

            # 建 email_records 表
            email_records_table = "email_records"
            cursor.execute(f"USE `{self.db_name}`;")
            cursor.execute("""SHOW TABLES;""")
            if email_records_table not in [
                _table[0].lower() for _table in cursor.fetchall()
            ]:
                logger.info(f"Table {email_records_table} does not exist, creating...")
                cursor.execute(
                    f"""CREATE TABLE IF NOT EXISTS {email_records_table} (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(255) NOT NULL COMMENT '邮件类型' COMMENT 'Email type',
            sender VARCHAR(255) NULL COMMENT '发件人邮箱地址' COMMENT 'Sender email address',
            recipient TEXT NOT NULL COMMENT '收件人邮箱地址' COMMENT 'Recipient email addresses',
            subject VARCHAR(255) NOT NULL COMMENT '邮件主题' COMMENT 'Email subject',
            body TEXT NOT NULL COMMENT '邮件正文内容' COMMENT 'Email body content',
            custom_data JSON NULL COMMENT '自定义数据（JSON格式）' COMMENT 'Custom data (JSON format)',
            scheduled_send_time DATETIME NULL COMMENT '计划发送时间' COMMENT 'Scheduled send time',
            status ENUM('pending', 'sent', 'failed', 'cancel') DEFAULT 'pending' COMMENT '发送状态：pending-待发送, sent-已发送, failed-发送失败, cancel-已取消' COMMENT 'Send status: pending-pending, sent-sent, failed-failed, cancel-cancel',
            actual_send_time DATETIME NULL COMMENT '实际发送时间' COMMENT 'Actual send time',
            callback_on_success VARCHAR(255) NULL COMMENT '发送成功回调地址' COMMENT 'Callback URL on success',
            callback_on_failure VARCHAR(255) NULL COMMENT '发送失败回调地址' COMMENT 'Callback URL on failure',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间' COMMENT 'Record creation time',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间' COMMENT 'Record update time'
        ) COMMENT='邮件发送记录' COMMENT='Email send records';"""
                )
                self.db.commit()

                # 添加复合索引
                logger.info("Adding composite index...")
                cursor.execute(
                    """CREATE INDEX idx_status_scheduled_time ON email_records (status, scheduled_send_time);"""
                )
                self.db.commit()

    def put_record(self, email: Email):
        with self.db.cursor() as cursor:
            cursor.execute(f"USE `{self.db_name}`;")

            # 处理收件人字段
            if isinstance(email.recipient, list):
                recipient = ",".join(email.recipient)
            else:
                recipient = email.recipient

            # 处理自定义数据字段
            custom_data = json.dumps(email.custom_data) if email.custom_data else None

            # 处理计划发送时间字段
            scheduled_send_time = (
                email.scheduled_send_time.strftime("%Y-%m-%d %H:%M:%S")
                if email.scheduled_send_time
                else None
            )

            # 插入记录
            query = """INSERT INTO email_records (
                type, subject, recipient, body, custom_data, scheduled_send_time, status, callback_on_success, callback_on_failure
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                email.type.value,
                email.subject,
                recipient,
                email.body,
                custom_data,
                scheduled_send_time,
                PENDING,  # 初始状态为 pending
                email.callback_on_success,
                email.callback_on_failure,
            )

            try:
                cursor.execute(query, values)
                self.db.commit()
                return cursor.lastrowid
            except pymysql.err.Error as e:
                self.db.rollback()
                message = f"Failed to insert record: {e}"
                logger.error(message)
                raise RuntimeError(message)

    def get_record(self, record_id: int = None):
        with self.db.cursor() as cursor:
            cursor.execute(f"USE `{self.db_name}`;")

            if record_id is not None:
                query = f"""SELECT * FROM email_records WHERE id={record_id}"""
                cursor.execute(query)
                result = cursor.fetchone()

                if result:
                    columns = [column[0] for column in cursor.description]
                    record_dict = {
                        key: (
                            json.loads(value)
                            if key == "custom_data" and isinstance(value, str)
                            else value
                        )
                        for key, value in zip(columns, result)
                    }
                    return record_dict
                return {}

            query = """SELECT *
            FROM email_records
            WHERE status IN ('pending')
             AND (scheduled_send_time <= NOW() OR scheduled_send_time IS NULL);"""
            cursor.execute(query)

            columns = [column[0] for column in cursor.description]
            records = [
                {
                    key: (
                        json.loads(value)
                        if key == "custom_data" and isinstance(value, str)
                        else value
                    )
                    for key, value in zip(columns, row)
                }
                for row in cursor.fetchall()
            ]
            self.db.commit()
            return {record["id"]: Email(**record) for record in records}

    def update_record(self, record_id: int, status: str, sender: str = None):
        with self.db.cursor() as cursor:
            cursor.execute(f"USE `{self.db_name}`;")
            try:
                if status == CANCEL:
                    query = f"""UPDATE email_records 
                SET status='{status}'
                WHERE id={record_id} AND status IN ('{PENDING}')"""
                else:
                    query = f"""UPDATE email_records 
                    SET status='{status}', 
                    actual_send_time=NOW(), 
                    sender='{sender}'
                    WHERE id={record_id}"""
                logger.debug(query)

                cursor.execute(query)
                self.db.commit()
                return cursor.rowcount
            except pymysql.err.Error as e:
                self.db.rollback()
                message = f"Failed to update record: {e}"
                logger.error(message)
                raise RuntimeError(message)


if __name__ == "__main__":
    pass
