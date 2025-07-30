from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json

import keyring
from platformdirs import user_config_dir

SERVICE = "price-check"


@dataclass
class Credentials:
    client_id: Optional[int]
    api_key: Optional[str]
    base_url: Optional[str]


def _config_path() -> Path:
    cfg_dir = Path(user_config_dir("price-check", "kashikuroni"))
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir / "config.json"


def load_credentials() -> Credentials:
    api_key = keyring.get_password(SERVICE, "OZON_API_KEY")
    client_id_str = keyring.get_password(SERVICE, "OZON_CLIENT_ID")

    client_id = (
        int(client_id_str) if client_id_str and client_id_str.isdigit() else None
    )

    base_url = None
    cfg_p = _config_path()
    if cfg_p.exists():
        try:
            data = json.loads(cfg_p.read_text(encoding="utf-8"))
            base_url = data.get("OZON_BASE_URL")
        except Exception:
            pass

    return Credentials(client_id=client_id, api_key=api_key, base_url=base_url)


def save_credentials(
    *,
    client_id: int,
    api_key: str,
    base_url: Optional[str] = "https://api-seller.ozon.ru",
) -> None:
    keyring.set_password(SERVICE, "OZON_API_KEY", api_key)
    keyring.set_password(SERVICE, "OZON_CLIENT_ID", str(client_id))
    cfg_p = _config_path()
    payload = {"OZON_BASE_URL": base_url} if base_url else {}
    cfg_p.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
