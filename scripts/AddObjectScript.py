"""
Creates a panel inside blender 3D view to add a cube or cylinder.
"""
import bpy


class TestPanel(bpy.types.Panel):
    """Test panel in 3D view.

    Parameters
    ----------
    bpy : bpy item
        Panel to create buttons
    """

    bl_label = "Test Panel"
    bl_idname = "PT_Test"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AddObject"

    def draw(self, context):
        """Makes the panel with labels and icons

        Parameters
        ----------
        context : bpy tpye
            current active scene
        """
        layout = self.layout

        row = layout.row()
        row.label(text="Add Object", icon="CUBE")
        row = layout.row()
        row.operator("mesh.primitive_cube_add")
        row.operator("mesh.primitive_cylinder_add")


def register():
    """Registers class"""
    bpy.utils.register_class(TestPanel)


def unregister():
    """Deregisters class"""
    bpy.utils.unregister_class(TestPanel)


if __name__ == "__main__":
    register()

# bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
