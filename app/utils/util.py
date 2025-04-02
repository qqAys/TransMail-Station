import logging
import os

import yaml

base_dir = os.path.dirname(os.path.abspath(__file__))
app_name = "TransMail-Station"
app_version = "0.0.3"


class Config:
    asgi_log_level = None
    app_log_level = None

    app_port = None
    app_database = None

    trusted_hosts = None
    valid_api_keys = None

    send_interval = None

    contact_lists = None
    mail_server = None

    def __init__(self):
        self.reinit()

    def reinit(self):
        os.makedirs(os.path.join(base_dir, "../../config"), exist_ok=True)

        if not os.path.exists(os.path.join(base_dir, "../../config/config.yml")):
            raise FileNotFoundError("config.yml File not exists")

        with open(
            os.path.join(base_dir, "../../config/config.yml"), "r", encoding="utf-8"
        ) as yml_file:
            config = yaml.safe_load(yml_file)
            self.asgi_log_level = config["asgi_log_level"]
            self.app_log_level = config["app_log_level"]

            self.app_port = config["app_port"]
            self.app_database = config["app_database"]

            self.trusted_hosts = config["trusted_hosts"]
            self.valid_api_keys = config["api_key"]

            self.send_interval = config["send_interval"]

            self.contact_lists = config["contact_lists"]
            self.mail_server = config["mail_server"]


class Logger:
    def __init__(self):
        """
        初始化 Logger 实例
        """
        config = Config()

        os.makedirs(os.path.join(base_dir, "../../logs"), exist_ok=True)
        log_file = os.path.join(base_dir, "../../logs/app.log")
        self.logger = logging.getLogger(app_name)
        level = config.app_log_level
        self.logger.setLevel(level.upper())

        formatter = logging.Formatter(
            '{"level": "%(levelname)s", "time": "%(asctime)s", "file": "%(filename)s", "line": %(lineno)d, "message": "%(message)s"}'
        )

        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 添加文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @staticmethod
    def _expand_message(message: str) -> str:
        return message.replace("\n", "[NEWLINE]").replace('"', "'")

    def debug(self, message: str):
        self.logger.debug(self._expand_message(message), stacklevel=2)

    def info(self, message: str):
        self.logger.info(self._expand_message(message), stacklevel=2)

    def warning(self, message: str):
        self.logger.warning(self._expand_message(message), stacklevel=2)

    def error(self, message: str):
        self.logger.error(self._expand_message(message), stacklevel=2)


logger = Logger()

if __name__ == "__main__":
    pass
