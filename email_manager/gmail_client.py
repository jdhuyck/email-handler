import datetime
import json
from math import trunc
from pathlib import Path
from typing import Optional

from app_confetti.fetch import dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from email_manager.config import Config


class TokenAuthentication:
    def __init__(self, scopes: list = ["https://mail.google.com/"]):
        self.scopes = scopes

    def gmail_authenticate(self, token: json):
        return build("gmail", "v1", credentials=Credentials.from_authorized_user_info(token))  # noqa:E501

    def create_token(self, client_config: dict, token_path: str):
        # Used to create gmail_token.json - only call in offline scripts
        creds = None
        token_file = Path(token_path)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config, self.scopes)  # noqa:E501
            creds = flow.run_local_server(port=0)

        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        with token_file.open("w") as token:
            json.dump(token_data, token)


class EmailFetcher:
    def __init__(self, token: json):
        self.service = TokenAuthentication.gmail_authenticate(self, token)

    def _parse_message(self, message):
        msg = self.service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        return msg

    def search_messages(self, service, query):
        result = service.users().messages().list(userId="me", q=query).execute()  # noqa:E501
        messages = []
        if "messages" in result:
            messages.extend(result["messages"])
        while "nextPageToken" in result:
            page_token = result["nextPageToken"]
            result = service.users().messages().list(userId="me", q=query, pageToken=page_token).execute()  # noqa:E501
            if "messages" in result:
                messages.extend(result["messages"])
        return messages

    def fetch_emails(
        self,
        since: datetime.datetime,
        before: Optional[datetime.datetime] = None
    ) -> list:
        query = f"after:{trunc(since.timestamp())}"
        if before is not None:
            query = f"{query} before:{trunc(before.timestamp())}"

        messages = self.search_messages(self.service, query)
        return [self._parse_message(msg) for msg in messages]


if __name__ == "__main__":
    # client = TokenAuthentication(["https://mail.google.com/"])
    # credentials = json.load(open("credentials/gmail_credentials.json", "rb"))
    # token = client.create_token(
    #     client_config=credentials,
    #     token_path="credentials/gmail_token.json")

    dotenv.fetch_to_env()
    settings = Config()

    token = json.load(open("credentials/gmail_token.json", "rb"))

    since = datetime.datetime.now(
        tz=datetime.timezone.utc) - datetime.timedelta(1)
    fetcher = EmailFetcher(token=token)

    emails = fetcher.fetch_emails(since)
