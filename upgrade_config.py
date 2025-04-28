import os

import yaml
from packaging import version

from app.utils.util import logger

env_version_key = "TRANSMAIL_STATION_VERSION"


def get_app_version_form_env():
    env_value = os.getenv(env_version_key)
    if env_value is None:
        EnvironmentError(f"{env_version_key} not set")
    return env_value


class UpgradeConfig:
    config = None
    should_upgrade = None

    def __init__(self):
        self.should_upgrade = False
        logger.info("Checking config.yml ...")

        with open("./config/config.yml", "r") as f:
            self.config = yaml.safe_load(f)
            config_version = self.config.get("app_version", None)
        logger.info(f"Current config version: {config_version}")

        self.upgrade_config(config_version)

        if self.should_upgrade is True:
            self.rewrite_config()
        else:
            logger.info("No need to upgrade config.yml.")

    def upgrade_config(self, current_config_version):

        if current_config_version == get_app_version_form_env():
            return

        # config_version is none or less than 0.0.5
        if current_config_version is None or version.parse(
                current_config_version
        ) <= version.parse("0.0.4"):
            logger.info("Upgrading config.yml ...")
            self.should_upgrade = True

            # update config version
            self.config["app_version"] = get_app_version_form_env()

            # update contact_lists, set contact_lists alias using the first mail_server alias name.
            contact_lists = self.config["contact_lists"]
            for key, value in contact_lists.items():
                first_mail = value[0]
                contact_lists[key] = {
                    "alias": self.config["mail_server"][first_mail]["alias"],
                    "mail": value,
                }

            # remove alias from mail_server
            for email, details in self.config["mail_server"].items():
                details.pop("alias", None)

            return

        if version.parse(current_config_version) < version.parse("0.0.6"):
            logger.info("Upgrading config.yml ...")
            self.should_upgrade = True

            # update config version
            self.config["app_version"] = get_app_version_form_env()

            return

    def rewrite_config(self):
        with open("./config/config.yml", "w") as f:
            yaml.safe_dump(self.config, f, allow_unicode=True, encoding="utf-8", sort_keys=False, default_flow_style=False)

        logger.info(f"Current config version: {self.config['app_version']}")
        logger.info("Rewrite config.yml Done.")

        self.__init__()


if __name__ == "__main__":
    UpgradeConfig()
