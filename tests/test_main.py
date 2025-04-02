import json
import unittest

import requests

from app.utils.util import Config

config = Config()

BASE_URL = f"http://localhost:{config.app_port}"


class TestAPIMethods(unittest.TestCase):

    def test_post_email(self):
        body = """<h1>TEST</h1>"""

        payload = json.dumps(
            {
                "to": "me@qqays.xyz",
                "subject": "TEST_EMAIL",
                "body": body,
                "callback_on_success": f"http://localhost:{config.app_port}/pass",
                "callback_on_failure": f"http://localhost:{config.app_port}/fail",
                "scheduled_send_time": "2025-01-01 00:00:00",
                "type": "notification",
                "custom_data": {},
            }
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.valid_api_keys[0]}",
        }

        response = requests.request(
            "POST", f"{BASE_URL}/send-email", headers=headers, data=payload
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result["code"], 200)


if __name__ == "__main__":
    unittest.main()
