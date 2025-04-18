import os

import yaml
from packaging import version

from app.utils.util import logger


class UpgradeConfig:
    config = None
    should_upgrade = False

    def __init__(self):
        logger.info("Checking config.yml ...")

        with open("./config/config.yml", "r") as f:
            self.config = yaml.safe_load(f)
            config_version = self.config.get("app_version", None)
        logger.info(f"Current config version: {config_version}")

        self.upgrade_config(config_version)

    def upgrade_config(self, current_config_version):

        # config_version is none or less than 0.0.5
        if current_config_version is None or version.parse(
            current_config_version
        ) <= version.parse("0.0.4"):
            logger.info("Upgrading config.yml ...")
            self.should_upgrade = True

            # update config version
            env_version_key = "TRANSMAIL_STATION_VERSION"
            self.config["app_version"] = os.getenv(env_version_key)
            if self.config["app_version"] is None:
                raise EnvironmentError(f"{env_version_key} not set")

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

        if self.should_upgrade is True:
            self.rewrite_config()
        else:
            logger.info("No need to upgrade config.yml.")

    def rewrite_config(self):
        with open("./config/config.yml", "w") as f:
            yaml.dump(self.config, f)

        logger.info(f"Current config version: {self.config['app_version']}")
        logger.info("Rewrite config.yml Done.")


if __name__ == "__main__":
    UpgradeConfig()
