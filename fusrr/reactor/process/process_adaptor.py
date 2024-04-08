import re
from typing import Any

from process.io.mfile import MFile


class ProcessParams:
    """..."""

    def __init__(self, process_mfile: MFile):
        self.mfile = process_mfile
        self._keys = set(process_mfile.data.keys())

    def __getattr__(self, name: str):
        return self.mfile.data[name].get_scan(-1)

    def __getitem__(self, name: str):
        return self.mfile.data[name].get_scan(-1)

    def get(self, name: str, default: Any = None):  # noqa: ANN401
        """Gets the value of the key with string s."""
        if self.has_key(name):
            return self[name]
        return default

    def get_with(self, s: str):
        """Gets the value of the key that matches (using regex)
        the pattern of string s.
        """
        k = self.get_key_with(s)
        return self[k]

    def get_key_with(self, rgx: str) -> str:
        """Gets the key that matches (using regex) the pattern of string s."""
        k = self.get_keys_with(rgx)
        if not k:
            raise KeyError(f"Key with {rgx} not found")
        return k[0]

    def get_keys_with(self, rgx: str | list[str]) -> list[str]:
        """Gets the keys that match (using regex) the pattern of string s."""
        if isinstance(rgx, str):
            rgx = [rgx]
        r = re.compile(r"^(" + "|".join(rgx) + ")$")
        return list(filter(r.match, self._keys))

    def n_keys_with(self, s: str) -> int:
        """Gets the number of keys that match (using regex)
        the pattern of string s.
        """
        return len(self.get_keys_with(s))

    def has_key(self, name: str) -> bool:
        """Checks if the key exists."""
        return name in self._keys

    def has_key_with(self, rgx: str) -> bool:
        """Checks if a key exists that matches (using regex)
        the pattern of string s.
        """
        return bool(self.get_keys_with(rgx))
