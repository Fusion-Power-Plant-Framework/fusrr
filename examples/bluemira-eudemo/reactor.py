from pathlib import Path
from fusrr.reactor.bluemira.base import get_scene


get_scene(Path(__file__).parent / "eudemo.gltf")
