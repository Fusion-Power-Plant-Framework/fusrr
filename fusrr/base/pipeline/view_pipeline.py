from __future__ import annotations

from fusrr.base.pipeline.pipeline import FusrrPipeline
from fusrr.base.scene import FusrrScene
from fusrr.blender.scene_tools import deselect_all


class FusrrViewPipeline(FusrrPipeline[FusrrScene]):
    """A FusrrViewPipeline defines a container with a deterministic ordering
    for constructing FusrrScene's.
    """

    def execute(self):
        """Execute this pipeline.

        This will execute every scene in this pipeline
        (in order), modifying the scene as it goes.
        """
        if not self._pipeline:
            return

        for scene in self._pipeline:
            scene.execute()
            deselect_all()

            self._world_state.add_scene(scene)
