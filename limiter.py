from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from secrets import token_urlsafe

import os
import logging


class LimitReq:
    def __init__(self, app):
        storage_uri = os.environ.get("LIMITER_STORAGE_URL", None)
        if storage_uri is None:
            storage_uri = "memory://"
            app.config["RATELIMIT_ENABLED"] = False
            logging.warning("LIMITER_STORAGE_URL not found, rate limiter is disabled")
        self.generate_bypasss_key()
        self.fetch_limit_config()
        self.fetch_white_list()
        timeout = os.environ.get("LIMITER_STORAGE_TIMEOUT", 30)
        self.flask_limit = Limiter(
            app, key_func=get_remote_address,
            storage_uri=storage_uri,
            storage_options={"connect_timeout": timeout}
        )
    
    def generate_bypasss_key(self):
        self.key = os.environ.get("LIMITER_BYPASS_KEY", token_urlsafe(20))
        print(f"Auth for current session: {self.key}")
    
    def fetch_limit_config(self):
        self.config = os.environ.get("LIMIT_REQUEST", "100/minute")

    def fetch_white_list(self):
        self.white_list = set(
            os.environ.get("LIMITER_WHITELIST", "127.0.0.1;localhost").split(";"))
