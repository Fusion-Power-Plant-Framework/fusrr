import re

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

    def get(self, name: str, default=None):
        if self.exists(name):
            return self[name]
        return default

    def get_with(self, s: str):
        k = self.get_key_with(s)
        return self[k]

    def get_key_with(self, s: str) -> str:
        k = self.get_keys_with(s)
        if not k:
            raise KeyError(f"Key with {s} not found")
        return k[0]

    def get_keys_with(self, s: str | list[str]) -> list[str]:
        if isinstance(s, str):
            s = [s]
        r = re.compile(r"^(" + "|".join(s) + ")$")
        return list(filter(r.match, self._keys))

    def n_keys_with(self, s: str) -> int:
        return len(self.get_keys_with(s))

    def exists(self, name: str) -> bool:
        return name in self._keys
