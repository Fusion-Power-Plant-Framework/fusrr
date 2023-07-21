"""
A file that stores the blender components of the reactor
"""


class BlenderComponent(abc.ABC):
    """Stores default functions for blender setup and renderings"""

    def render_component_mesh(self):  # Currently used just for plasma
        """Sets up scene in which to build mesh + builds new mesh"""
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = None

        mesh = bpy.data.meshes.new("line_mesh")
        line_obj = bpy.data.objects.new("line_object", mesh)
        scene.collection.objects.link(line_obj)
        scene.view_layers.update()

        bm = bmesh.new()

        return scene, mesh, bm

    def tracking_centre(
        self, component_shape
    ):  # not great but gives a view that should include all components
        """Uses rmajor to make set of coordinates - Can be useful for camera tracking"""
        x, y = 0, component_shape.rmajor
        z = 6 * component_shape.rmajor
        return x, y, z

    def scene(self, x, y, z):
        """Sets up camera for rendering"""
        bt.delete_cube()
        bt.empty_obj(x, y, 0)
        bt.move_camera(x, y, z)
        bt.camera_fix("Camera", "Empty")

    def component_outline(self, coords):
        """Renders the spline of component (currently only used for tf coil)

        Parameters
        ----------
        x_coords : numpy array
        y_coords : numpy array

        """
        curve = bpy.data.curves.new(name="Curve_test", type="CURVE")
        curve.fill_mode = "NONE"

        ob = bpy.data.objects.new(name="TestObject", object_data=curve)
        scene = bpy.context.scene
        scene.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = None

        spline = curve.splines.new(type="POLY")
        spline.points.add(len(coords) - 1)
        for i, point in enumerate(spline.points):
            point.co[0:2] = coords[i]

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

        return None

    def hex_color_to_rgba(self, hex_color):
        """Converts hex to blender's sRGB"""
        hex_color = hex_color[1:]
        red = int(hex_color[:2], 16)
        srgb_red = red / 255

        green = int(hex_color[2:4], 16)
        srgb_green = green / 255

        blue = int(hex_color[4:6], 16)
        srgb_blue = blue / 255

        return tuple([srgb_red, srgb_green, srgb_blue, 1.0])

    def default_colour(self, colour):
        """Creates material to add colour to active objects(s)"""
        bpy.ops.object.select_all(action="SELECT")
        active_objects = bpy.context.selected_objects
        # h = input('Enter hex: ').lstrip('#')
        # RGB = (tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))
        if colour is None:
            colour = self.hex_color_to_rgba("#7d2f8e")
        else:
            colour = self.hex_color_to_rgba(colour)
        for object in active_objects:
            try:
                mat = bpy.data.materials.new(name="MatName")
                object.data.materials.append(mat)
                mat.diffuse_color = colour
                bpy.context.scene.view_layers.update()
            except AttributeError:
                continue


class Plasma(BlenderComponent):
    """Contains methods for plotting and rendering different parts of the plasma"""

    def __init__(self, plasma_shape):
        self.plasma_shape = plasma_shape
        # print(dir(self))

    @staticmethod
    def create_shape(plasma_shape):
        """Generates coordinates for the plasma boundary arcs

        Arguments:
        ---------
            plasma_shape: input values for componets
        """
        r0 = plasma_shape.rmajor
        a = plasma_shape.rminor
        delta = 1.5 * plasma_shape.delta_95
        kappa = (1.1 * plasma_shape.kappa95) + 0.04
        i_single_null = plasma_shape.i_single_null

        x1 = (2.0 * r0 * (1.0 + delta) - a * (delta**2 + kappa**2 - 1.0)) / (
            2.0 * (1.0 + delta)
        )
        x2 = (2.0 * r0 * (delta - 1.0) - a * (delta**2 + kappa**2 - 1.0)) / (
            2.0 * (delta - 1.0)
        )
        r1 = 0.5 * math.sqrt(
            (a**2 * ((delta + 1.0) ** 2 + kappa**2) ** 2) / ((delta + 1.0) ** 2)
        )
        r2 = 0.5 * math.sqrt(
            (a**2 * ((delta - 1.0) ** 2 + kappa**2) ** 2) / ((delta - 1.0) ** 2)
        )
        theta1 = np.arcsin((kappa * a) / r1)
        theta2 = np.arcsin((kappa * a) / r2)
        inang = 1.0 / r1
        outang = 1.5 / r2
        if i_single_null == 0:
            angs1 = np.linspace(
                -(inang + theta1) + np.pi, (inang + theta1) + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(
                -(outang + theta2), (outang + theta2), 256, endpoint=True
            )
        elif i_single_null < 0:
            angs1 = np.linspace(
                -(inang + theta1) + np.pi, theta1 + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(-theta2, (outang + theta2), 256, endpoint=True)
        else:
            angs1 = np.linspace(
                -theta1 + np.pi, (inang + theta1) + np.pi, 256, endpoint=True
            )
            angs2 = np.linspace(-(outang + theta2), theta2, 256, endpoint=True)

        xs1 = -(r1 * np.cos(angs1) - x1)
        ys1 = r1 * np.sin(angs1)
        xs2 = -(r2 * np.cos(angs2) - x2)
        ys2 = r2 * np.sin(angs2)

        return xs1, xs2, ys1, ys2

    def render(self, x_coords, y_coords):
        """Renders the vertices of the plasma array for plasma mesh

        Parameters
        ----------
        x_coords : numpy array
        y_coords : numpy array

        """
        scene, mesh, bm = self.render_component_mesh()

        for x, y in zip(x_coords, y_coords):
            bm.verts.new((x, y, 0))

        bm.to_mesh(mesh)
        bm.free()

        scene.view_layers.update()
        return None

    @staticmethod
    def plasma_centre(
        x1, x2, y1, y2
    ):  # General, should be able to apply to most components - depending on plotting
        """Calculates centre of plasma for tracking"""
        half_arr = int(len(x1) / 2)
        half_x = x1[half_arr] - x2[half_arr]
        half_y = y1[half_arr] - y2[half_arr]

        return half_x, half_y

    def setup_scene(self, x_coords, y_coords, z_coords):
        """Sets up cameras and objects for rendering"""
        self.scene(x_coords, y_coords, z_coords)
        object_list = [
            "line_object",
            "line_object.001",
        ]  # is there a way to automate naming of objects?
        bt.join_obj(object_list)
        bt.make_face_from_vertices("line_object")

    def build(self):
        """Combines above functions to plot, track and render plasma"""
        xs1, xs2, ys1, ys2 = self.create_shape(self.plasma_shape)
        x, y = self.plasma_centre(xs1, xs2, ys1, ys2)
        self.render(xs1, ys2)
        self.render(xs2, ys2)
        self.default_colour(colour=None)
        self.setup_scene(x, y, 0)


class TFCoil(BlenderComponent):
    """Contains method for plotting and rendering tf coils"""

    def __init__(self, tf_coil_shape):
        self.tf_coil_shape = tf_coil_shape

    def create_shape(self):  # was plot_tf_coils
        """Function to plot TF coils
        Arguments:
        --------
            axis --> axis object to plot to
            mfile_data --> MFILE.DAT object
            scan --> scan number to use
        """
        # Arc points
        # MDK Only 4 points now required for elliptical arcs

        tfc_inleg = self.tf_coil_shape.tfc_inleg
        rtangle = np.pi / 2
        x1 = self.tf_coil_shape.x1
        y1 = self.tf_coil_shape.y1
        x2 = self.tf_coil_shape.x2
        y2 = self.tf_coil_shape.y2
        x3 = self.tf_coil_shape.x3
        y3 = self.tf_coil_shape.y3
        x4 = self.tf_coil_shape.x4
        y4 = self.tf_coil_shape.y4
        x5 = self.tf_coil_shape.x5
        y5 = self.tf_coil_shape.y5
        if y3 != 0:
            print("TF coil geometry: The value of yarc(3) is not zero, but should be.")

        x0 = x2
        y0 = y1
        a1 = x2 - x1
        b1 = y2 - y1
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1,
            a2=a2,
            b1=b1,
            b2=b2,
            x0=x0,
            y0=y0,
            ang1=rtangle,
            ang2=2 * rtangle,
        )
        self.component_outline(verts)
        # Outboard upper arc
        x0 = x2
        y0 = 0
        a1 = x3 - x2
        b1 = y2
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=0, ang2=rtangle
        )
        self.component_outline(verts)
        # Inboard lower arc
        x0 = x4
        y0 = y5
        a1 = x4 - x5
        b1 = y5 - y4
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=-rtangle, ang2=-2 * rtangle
        )
        self.component_outline(verts)
        # Outboard lower arc
        x0 = x4
        y0 = 0
        a1 = x3 - x2
        b1 = -y4
        a2 = a1 + tfc_inleg
        b2 = b1 + tfc_inleg
        verts = ellips_fill(
            a1=a1, a2=a2, b1=b1, b2=b2, x0=x0, y0=y0, ang1=0, ang2=-rtangle
        )
        self.component_outline(verts)
        # Vertical leg
        # Bottom left corner
        rect = patches.Rectangle(
            [x5 - tfc_inleg, y5], tfc_inleg, (y1 - y5), lw=0, facecolor="cyan"
        )
        centre_coords = bt.rect_blend(rect)
        self.component_outline(centre_coords)

    def setup_scene(self):
        """Sets up scene and objects for rendering"""
        x, y, z = self.tracking_centre(self.tf_coil_shape)
        self.scene(x, y, z)  # Tracking works but is wonky
        object_list = [
            "TestObject",
            "TestObject.001",
            "TestObject.002",
            "TestObject.003",
            "TestObject.004",
        ]

        bt.change_to_mesh(object_names=object_list)
        for i in object_list:
            bt.make_face_from_vertices(str(i))

        # print(dir(self))

    def build(self):
        """Plots tracks and renders tf coils"""
        self.create_shape()
        self.setup_scene()
        self.default_colour(colour="#0072c2")
