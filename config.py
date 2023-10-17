import os

import environ

SECRETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secrets.ini")
ENVIRONMENT = os.environ.get("ENVIRONMENT", default="testing")
ini_secrets = environ.secrets.INISecrets.from_path(SECRETS_PATH, ENVIRONMENT)


@environ.config(prefix="")
class Config:
    secret_key = ini_secrets.secret(name="spotify_secret")

    @environ.config(prefix="SPOTIFY")
    class Spotify:
        id = ini_secrets.secret(name="spotify_client_id")
        secret = ini_secrets.secret(name="spotify_secret")
        rate_limit_tokens = 60
        rate_limit_period = 60

    spotify = environ.group(Spotify)


cfg: Config = Config.from_environ()
