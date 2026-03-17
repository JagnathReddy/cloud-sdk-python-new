from typing import Optional, List

class Config:
    def __init__(self, id: str, blocked_file_extensions: Optional[List[str]] = None, tempspace_max_content_size: Optional[int] = None, is_cross_domain_mapping_allowed: Optional[bool] = None):
        self.id = id
        self.blocked_file_extensions = blocked_file_extensions or []
        self.tempspace_max_content_size = tempspace_max_content_size
        self.is_cross_domain_mapping_allowed = is_cross_domain_mapping_allowed
