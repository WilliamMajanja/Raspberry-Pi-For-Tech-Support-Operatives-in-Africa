"""Small, loopback-only adapter to CPIP's authenticated CoffeeCipher endpoints."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request


class CPIPAdapterError(Exception):
    """CPIP integration failure with no secret material in the message."""


class CPIPAdapter:
    """Call CPIP's local covert-encoding API; never send the CPIP key remotely."""

    ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}
    MAX_RESPONSE_BYTES = 64 * 1024
    MAX_CIPHER_CHARS = 16 * 1024

    def __init__(self, origin: str, covert_key: str, timeout: float = 5.0):
        parsed = urllib.parse.urlsplit(origin)
        if parsed.scheme != "http" or parsed.hostname not in self.ALLOWED_HOSTS:
            raise CPIPAdapterError("CPIP backend must be plain HTTP on loopback only; public TLS belongs at the portal proxy.")
        if parsed.path not in ("", "/") or parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise CPIPAdapterError("CPIP internal origin must contain only loopback scheme, host, and port.")
        if not covert_key or covert_key == "CHANGE_ME_COFFEE_BLEND_2024" or len(covert_key.encode("utf-8")) < 32:
            raise CPIPAdapterError("A persistent CPIP_COVERT_KEY of at least 32 bytes is required.")
        self.origin = f"http://{parsed.netloc}"
        self.key = covert_key.encode("utf-8")
        self.timeout = timeout

    def _post(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        if path not in {"/cpip/mesh/encode", "/cpip/mesh/decode"}:
            raise CPIPAdapterError("Refusing an unapproved CPIP endpoint.")
        timestamp = str(int(time.time()))
        mac = hmac.new(self.key, f"{timestamp}:POST:{path}".encode("utf-8"), hashlib.sha256).hexdigest()
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            self.origin + path,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-CPIP-HMAC": f"{timestamp}:{mac}",
            },
            method="POST",
        )
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(request, timeout=self.timeout) as response:
                if urllib.parse.urlsplit(response.geturl()).netloc != urllib.parse.urlsplit(self.origin).netloc:
                    raise CPIPAdapterError("CPIP backend changed origin; refusing response.")
                raw = response.read(self.MAX_RESPONSE_BYTES + 1)
        except urllib.error.HTTPError as error:
            raise CPIPAdapterError(f"CPIP rejected the local cipher operation (HTTP {error.code}).") from None
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise CPIPAdapterError(f"CPIP loopback service unavailable: {error.reason if isinstance(error, urllib.error.URLError) else error}") from None
        if len(raw) > self.MAX_RESPONSE_BYTES:
            raise CPIPAdapterError("CPIP response exceeded the size limit.")
        try:
            result = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise CPIPAdapterError("CPIP returned invalid JSON.") from None
        if not isinstance(result, dict):
            raise CPIPAdapterError("CPIP returned an unexpected response type.")
        return result

    def encode_token(self, edition_id: str, token: str) -> str:
        if not re.fullmatch(r"[a-f0-9]{24}", edition_id):
            raise CPIPAdapterError("Invalid edition identifier.")
        if not token or len(token) > 256 or "\n" in token or "\r" in token:
            raise CPIPAdapterError("Invalid edition token.")
        message = json.dumps(
            {"v": 1, "purpose": "cpip-book-edition", "edition_id": edition_id, "token": token},
            separators=(",", ":"),
            sort_keys=True,
        )
        result = self._post("/cpip/mesh/encode", {"message": message, "recipe": "espresso", "ecc": False})
        cipher = result.get("accept_additions_header")
        if result.get("status") != "encoded" or not isinstance(cipher, str) or not cipher:
            raise CPIPAdapterError("CPIP did not produce a Coffee Cipher.")
        if len(cipher) > self.MAX_CIPHER_CHARS or "\r" in cipher or "\n" in cipher:
            raise CPIPAdapterError("CPIP produced an invalid or oversized cipher.")
        return cipher

    def decode_token(self, cipher: str) -> tuple[str, str]:
        if not cipher or len(cipher) > self.MAX_CIPHER_CHARS or "\r" in cipher or "\n" in cipher:
            raise CPIPAdapterError("Invalid Coffee Cipher format.")
        result = self._post("/cpip/mesh/decode", {"accept_additions": cipher})
        if result.get("status") != "decoded" or not isinstance(result.get("message"), str):
            raise CPIPAdapterError("Coffee Cipher could not be decoded.")
        try:
            payload = json.loads(result["message"])
        except json.JSONDecodeError:
            raise CPIPAdapterError("Coffee Cipher payload is invalid.") from None
        if not isinstance(payload, dict) or payload.get("v") != 1 or payload.get("purpose") != "cpip-book-edition":
            raise CPIPAdapterError("Coffee Cipher is not a book-edition credential.")
        edition_id = payload.get("edition_id")
        token = payload.get("token")
        if not isinstance(edition_id, str) or not re.fullmatch(r"[a-f0-9]{24}", edition_id):
            raise CPIPAdapterError("Coffee Cipher contains an invalid edition ID.")
        if not isinstance(token, str) or not token or len(token) > 256:
            raise CPIPAdapterError("Coffee Cipher contains an invalid token.")
        return edition_id, token
