import dataclasses

from app_confetti import util


def optional_str(v):
    return v if v.lower() != "none" else None

@dataclasses.dataclass
class Config:
    gmail_token: str = util.env("GMAIL_TOKEN: None", optional_str)
    gmail_refresh_token: str = util.env("GMAIL_REFRESH_TOKEN:None", optional_str)
    gmail_client_id: str = util.env("GMAIL_CLIENT_ID:None", optional_str)
    gmail_client_secret: str = util.env("GMAIL_CLIENT_SECRET", optional_str)

    @property
    def gmail_token_json(self):
        if self.gmail_token is not None:
            return {
                "token": self.gmail_token,
                "refresh_token": self.gmail_refresh_token,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": self.gmail_client_id,
                "client_secret": self.gmail_client_secret,
                "scopes": ["https://mail.google.com/"],
            }
        else:
            return {}
