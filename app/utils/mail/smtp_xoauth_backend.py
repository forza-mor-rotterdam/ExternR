import requests
from django.conf import settings
from django.core.cache import cache
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address


class CustomEmailBackend(EmailBackend):
    def __init__(self, fail_silently=..., **kwargs):
        super().__init__(fail_silently, **kwargs)

    def open(self):
        # The username and passwords field will contain the client id and secret, save them in the right variabels
        self.client_id = self.username
        self.client_secret = self.password

        # Remove the username and password, this prevent that the EmailBackend will not start basic auth
        self.username = None
        self.password = None

        # Run the super version of this method, because no auth is given we need manualy call the helo() on the connection
        super().open()
        self.connection.helo()

        # Authentication is done in the _send method, because we need te from-address to complete authentication

        return True

    def _send(self, email_message):
        # Extract the from address from the message
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)

        def tokenGen(input=None):
            access_token = cache.get("access_token__" + from_email)
            if access_token is None:
                # Request a new access token
                response = requests.post(
                    url=settings.EMAIL_XOAUTH2_TOKEN_ENDPOINT,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": settings.EMAIL_XOAUTH2_SCOPE,
                    },
                )

                # Check status code
                if response.status_code != 200:
                    raise Exception(
                        "Could not exchange access token, code="
                        + str(response.status_code)
                        + ", body="
                        + str(response.content)
                    )
                response_data = response.json()
                access_token = response_data["access_token"]
                cache.set(
                    "access_token__" + self.client_id,
                    access_token,
                    response_data["expires_in"] - 10,
                )

            # Build xoauth2 string
            seperator = chr(1)
            return (
                "user="
                + from_email
                + seperator
                + "auth=Bearer "
                + access_token
                + seperator
                + seperator
            )

        res = self.connection.auth("XOAUTH2", tokenGen, initial_response_ok=True)
        if str(res[0]) != "235":
            raise Exception(
                "Access token not accepted or access token is not allowed for mailbox"
            )

        return super()._send(email_message)
