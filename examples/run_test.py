from pathlib import Path
from fusrr.reactor import Reactor
from fusrr.views import View

# from IPython.display import Image
p = Path(__file__).parent / "input-files/large_tokamak_MFILE.DAT"
example_reactor = Reactor.reactor_from_file(p)

example_view = View(example_reactor)
example_view.save_image("example_view_reactor")

# Image(url="example_view_reactor.png")
