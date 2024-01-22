import bpy
import os
import random

# Definisem direktorijum gde se nalaze fajlovi
root_folder = bpy.path.abspath('//')

# Definisem glavnu funkciju koja priprema fajlove za uvoz
def prepare_files_for_import():
    # Lista za cuvanje putanja do fajlova
    file_paths = []

    for file in os.listdir(root_folder):
        if file.endswith('.xyz') or file.endswith('.ply'):
            file_paths.append(os.path.join(root_folder, file))

    return file_paths

def replace_points_with_cubes(file_path):
    # Otvaram .xyz fajl
    with open(file_path, 'r') as file:
        points = file.readlines()

    cubes = []

    # Dodajem kocku za svaku 100. tacku
    for i in range(0, len(points), 100):
        x, y, z = float(points[i].split()[0]), float(points[i].split()[1]), float(points[i].split()[2])
        if x > 100: x /= 100
        if y > 100: y /= 100
        if z > 100: z /= 100
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
        cube = bpy.context.active_object
        # Smanjujem scale kocke da bi se videlo
        cube.scale = (cube.scale[0]/20, cube.scale[1]/20, cube.scale[2]/20)
        cubes.append(cube)

    return cubes

# Blender import UI 
class ImportFilesOperator(bpy.types.Operator):
    bl_idname = "import_files.operator"
    bl_label = "Operator za uvoz fajlova"

    # Definisem integer
    num_files: bpy.props.IntProperty(name="Broj fajlova za uvoz")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        # Pripremam fajlove za uvoz
        files_to_import = prepare_files_for_import()

        # Random odabiram broj fajlove u odnosu na integer 
        files_to_import = random.sample(files_to_import, min(self.num_files, len(files_to_import)))

        # Pravim novu kolekciju za .xyz fajlove
        xyz_collection = bpy.data.collections.new(name="XYZ")
        bpy.context.scene.collection.children.link(xyz_collection)

        # Pravim novu kolekciju za .ply fajlove
        ply_collection = bpy.data.collections.new(name="PLY")
        bpy.context.scene.collection.children.link(ply_collection)

        # Pravim novu kolekciju za objekte Convex Hull
        ch_collection = bpy.data.collections.new(name="CH")
        bpy.context.scene.collection.children.link(ch_collection)


        # Uvezem odabrane fajlove
        for file_path in files_to_import:
            if file_path.endswith('.xyz'):
                cubes = replace_points_with_cubes(file_path)
                for cube in cubes:
                    xyz_collection.objects.link(cube)
                    bpy.context.collection.objects.unlink(cube)
            elif file_path.endswith('.ply'):
                bpy.ops.import_mesh.ply(filepath=file_path)
                ply_object1 = bpy.context.active_object
                ply_collection.objects.link(ply_object1)
                bpy.context.collection.objects.unlink(ply_object1)

                # Kopiram ply fajl 
                bpy.ops.object.duplicate()
                bpy.ops.object.duplicate()
                
                # Stavljam nov fajl u CH kolekciju
                # Brisem ga iz PLY kolekcije
                ch_object = bpy.context.active_object
                ch_collection.objects.link(ch_object)
                ply_collection.objects.unlink(ch_object)

                # Odradjujem Convex Hull na novom objektu
                bpy.context.view_layer.objects.active = ch_object
                bpy.ops.object.mode_set(mode='EDIT') 
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.convex_hull()
                bpy.ops.object.mode_set(mode='OBJECT')
                
        # Selektuj sve kocke u kolekciji
        for obj in xyz_collection.objects:
            obj.select_set(True)

        # Postavite aktivni objekat na prvu kocku
        if len(xyz_collection.objects) > 0:
            bpy.context.view_layer.objects.active = xyz_collection.objects[0]
        else:
            print("No objects in XYZ collection")

        # Merge sve izabrane objekte
        if len(bpy.context.selected_objects) > 0:
            bpy.ops.object.join()
        else:
            print("No objects selected for merging")

        return {'FINISHED'}

# Registrujte operatora
bpy.utils.register_class(ImportFilesOperator)

# Pozovite operatora
bpy.ops.import_files.operator('INVOKE_DEFAULT', num_files=3)