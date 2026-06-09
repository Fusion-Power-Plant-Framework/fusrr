from __future__ import annotations

from typing import TYPE_CHECKING

from examples.process_eudemo.components.blanket import Blanket
from examples.process_eudemo.components.cryostat import Cryostat
from examples.process_eudemo.components.pf_coils import PFCoils
from examples.process_eudemo.components.plasma import Plasma
from examples.process_eudemo.components.tf_coils import TFCoils
from examples.process_eudemo.components.vacuum_vessel import VacuumVessel
from examples.process_eudemo.providers import process_params_provider
from fusrr import component
from fusrr.hooks import useSetProvider
from fusrr.modelling.blender import BlenderCompound
from fusrr.modelling.blender.tools.ops_tools import translate_selected
from fusrr.modelling.blender.tools.scene_tools import (
    deselect_all,
    select_collection_all_objects,
)

if TYPE_CHECKING:
    from os import PathLike
    from fusrr.core.vectors import Vec3


class EUDEMO_Compound(BlenderCompound):  # noqa: N801
    """Compound for the EUDEMO reactor components."""

    def __init__(self, components, *, translation: Vec3 | None = None):
        super().__init__(components)
        self.translation = translation

    def post_build(self, name: str, scene):
        super().post_build(name, scene)
        deselect_all()
        if self.translation:
            select_collection_all_objects(self.b_collection_name)
            translate_selected(self.translation)
            deselect_all()


@component
def EUDEMO_Reactor(mfile_filepath: PathLike, translation: Vec3 | None = None):
    """A component for creating an EUDEMO Reactor."""
    useSetProvider(process_params_provider, mfile_filepath)

    return EUDEMO_Compound(
        [
            Plasma(),
            Blanket(),
            VacuumVessel(),
            PFCoils(),
            TFCoils(),
            Cryostat(),
        ],
        translation=translation,
    )
