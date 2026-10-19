import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    session_ttl_seconds: int = 86400

    @classmethod
    def from_env(cls) -> 'Settings':
        ttl = int(os.environ.get('SESSION_TTL_SECONDS', '86400'))
        if not 1 <= ttl <= 31536000:
            raise ValueError('SESSION_TTL_SECONDS must be between 1 and 86400')
        return cls(session_ttl_seconds=ttl)
