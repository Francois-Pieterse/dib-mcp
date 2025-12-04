import re
import requests

from env_variables import get_env


class DibClientAuth:
    """Handles login and session reuse against Dropinbase."""

    TIMEOUT_SECONDS = int(10)

    def __init__(
        self,
        username: str,
        password: str,
        login_page_url: str,
        login_endpoint_url: str,
    ) -> None:
        # Create a session to persist cookies across requests
        self.session = requests.Session()

        # Store credentials - neceseary for more secure implementations?
        self.username = username
        self.password = password

        # URLs for login
        self.login_page_url = login_page_url
        self.login_endpoint_url = login_endpoint_url

        # Since the assumption is made that this will be run in a local trusted environment,
        # disable SSL verification to avoid issues with self-signed certificates.
        self.session.verify = False

    @property
    def has_session(self) -> bool:
        return self.session.cookies.get("PHPSESSID") is not None
    
    def set_session_id(self, phpsessid: str) -> None:
        """Manually set the PHPSESSID cookie to use an existing session."""
        self.session.cookies.set("PHPSESSID", phpsessid)

    def _fetch_form_token(self) -> str:
        """Fetch the form_token from the login page HTML."""
        response = self.session.get(self.login_page_url, timeout=self.TIMEOUT_SECONDS)
        response.raise_for_status()

        login_page_html = response.text
        match = re.search(r'name="form_token"[^>]*?value="([^"]+)"', login_page_html)
        if not match:
            raise RuntimeError("Could not find form_token in login page HTML")

        return match.group(1)

    def login(self) -> None:
        """Perform login to obtain a valid session."""
        form_token = self._fetch_form_token()

        payload = {
            "username": self.username,
            "password": self.password,
            "email1": "",
            "form_token": form_token,
        }

        resp = self.session.post(
            self.login_endpoint_url, data=payload, timeout=self.TIMEOUT_SECONDS
        )
        resp.raise_for_status()

        if not self.has_session:
            raise RuntimeError("Login succeeded but PHPSESSID cookie was not set")

    def ensure_logged_in(self) -> None:
        """Ensure that there is a valid logged-in session."""
        if not self.has_session:
            self.login()

    def request(self, method: str, url: str, *, headers: dict | None = None, **kwargs):
        """
        Make an authenticated request. If one of the RETRY codes are received (e.g. 419),
        assume the session expired, clear cookies, log in again, retry once.
        """
        self.ensure_logged_in()

        resp = self.session.request(
            method, url, headers=headers, timeout=self.TIMEOUT_SECONDS, **kwargs
        )

        AUTH_AND_RETRY_CODES = [419, 401]
        if resp.status_code in AUTH_AND_RETRY_CODES:
            # Likely expired session, clear cookies and retry once with a fresh login
            self.session.cookies.clear()
            self.login()
            resp = self.session.request(
                method, url, headers=headers, timeout=self.TIMEOUT_SECONDS, **kwargs
            )

        return resp


# Create a global instance
dib_session_client = DibClientAuth(
    username=get_env("DIB_USERNAME", "admin"),
    password=get_env("DIB_PASSWORD", "test"),
    login_page_url=get_env(
        "DIB_LOGIN_PAGE_URL",
        f"{get_env('BASE_URL', 'https://localhost')}/login",
    ),
    login_endpoint_url=get_env(
        "DIB_LOGIN_ENDPOINT_URL",
        f"{get_env('BASE_URL', 'https://localhost')}/dropins/dibAuthenticate/Site/login",
    ),
)
