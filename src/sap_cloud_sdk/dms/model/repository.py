from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class RepositoryParam:
    param_name: str
    param_value: Any

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RepositoryParam:
        return cls(
            param_name=data.get("paramName", ""),
            param_value=data.get("paramValue")
        )


@dataclass
class Repository:
    id: Optional[str] = None
    cmis_repository_id: Optional[str] = None
    name: Optional[str] = None
    repository_type: Optional[str] = None
    repository_sub_type: Optional[str] = None
    repository_category: Optional[str] = None
    created_time: Optional[datetime] = None
    last_updated_time: Optional[datetime] = None
    repository_params: List[RepositoryParam] = field(default_factory=list)
    _params_lookup: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        params: List[RepositoryParam] = self.repository_params
        self._params_lookup: Dict[str, Any] = {
            p.param_name: p.param_value for p in params
        }

    def _get_param(self, name: str) -> Any:
        return self._params_lookup.get(name)


   # values taken from params list
    @property
    def is_version_enabled(self) -> Optional[bool]:
        return self._get_param("isVersionEnabled")

    @property
    def is_virus_scan_enabled(self) -> Optional[bool]:
        return self._get_param("isVirusScanEnabled")

    @property
    def is_thumbnail_enabled(self) -> Optional[bool]:
        return self._get_param("isThumbnailEnabled")

    @property
    def is_encryption_enabled(self) -> Optional[bool]:
        return self._get_param("isEncryptionEnabled")

    @property
    def is_client_cache_enabled(self) -> Optional[bool]:
        return self._get_param("isClientCacheEnabled")

    @property
    def is_ai_enabled(self) -> Optional[bool]:
        return self._get_param("isAIEnabled")

    @property
    def is_async_virus_scan_enabled(self) -> Optional[bool]:
        return self._get_param("isAsyncVirusScanEnabled")

    @property
    def skip_virus_scan_for_large_file(self) -> Optional[bool]:
        return self._get_param("skipVirusScanForLargeFile")

    @property
    def hash_algorithms(self) -> Optional[str]:
        return self._get_param("hashAlgorithms")

    @property
    def change_log_duration(self) -> Optional[int]:
        return self._get_param("changeLogDuration")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Repository:
        # ✅ typed variable — pins type of p in the comprehension
        params_raw: List[Dict[str, Any]] = data.get("repositoryParams") or []

        return cls(
            id=data.get("id"),
            cmis_repository_id=data.get("cmisRepositoryId"),
            name=data.get("name"),
            repository_type=data.get("repositoryType"),
            repository_sub_type=data.get("repositorySubType"),
            repository_category=data.get("repositoryCategory"),
            created_time=_parse_datetime(data.get("createdTime")),
            last_updated_time=_parse_datetime(data.get("lastUpdatedTime")),
            repository_params=[RepositoryParam.from_dict(p) for p in params_raw],
        )

    def __repr__(self) -> str:
        return (
            f"Repository(id={self.id!r}, name={self.name!r}, "
            f"type={self.repository_type!r}, "
            f"category={self.repository_category!r})"
        )


def _parse_datetime(val: Any) -> Optional[datetime]:
    if val is None:
        return None
    if isinstance(val, int):
        return datetime.fromtimestamp(val / 1000, tz=timezone.utc) # assuming milliseconds
    return datetime.fromisoformat(str(val).replace("Z", "+00:00")) 