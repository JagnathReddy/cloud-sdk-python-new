from sap_cloud_sdk.dms._models import DMSCredentials


class DMSClient:
    """Client for interacting with the DMS service."""

    def __init__(self, credentials: DMSCredentials):
        """Initialize the DMS client with provided credentials.

        Args:
            credentials: DMSCredentials constructed from either BindingData or directly with required fields.
        """
        #fetch access token
        try:
            credentials.access_token
        except Exception as e:
            raise ValueError(f"Failed to fetch access token: {e}")
        
        self.credentials = credentials
        self._admin = None  # Lazy initialization of AdminService

    @property
    def admin(self) -> AdminService:
        if self._admin is None:
            self._admin = AdminService(self._base_url, self._token_manager)
        return self._admin