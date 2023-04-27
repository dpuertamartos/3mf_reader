import os
import Lib3MF


#TO EDIT
FILE_NAME = "triangle.3mf"
#STOP EDITING

PATH = "./samples/"
FILE = PATH + FILE_NAME
libpath = './lib3mf_sdk_v2.2.0/Bin'
lib3mf = Lib3MF.Wrapper(os.path.join(libpath, "lib3mf"))
major, minor, micro = lib3mf.GetLibraryVersion()
print("Lib3MF version: {:d}.{:d}.{:d}".format(major, minor, micro), end="")

'''helpers'''
def show_metadata_information(meta_data_group):
    n_meta_data_count = meta_data_group.GetMetaDataCount()

    for i_meta in range(n_meta_data_count):
        meta_data = meta_data_group.GetMetaData(i_meta)
        s_meta_data_value = meta_data.GetValue()
        s_meta_data_name = meta_data.GetName()

        print(f"Metadatum: {i_meta}:")
        print(f"Name  = \"{s_meta_data_name}\"")
        print(f"Value = \"{s_meta_data_value}\"")

def show_slice_stack(slice_stack, indent):
    print(f"{indent}SliceStackID:  {slice_stack.GetResourceID()}")
    if slice_stack.GetSliceCount() > 0:
        print(f"{indent}  Slice count:  {slice_stack.GetSliceCount()}")
    if slice_stack.GetSliceRefCount() > 0:
        print(f"{indent}  Slice ref count:  {slice_stack.GetSliceRefCount()}")
        for i_slice_ref in range(slice_stack.GetSliceRefCount()):
            print(f"{indent}  Slice ref :  {slice_stack.GetSliceStackReference(i_slice_ref).GetResourceID()}")


def show_object_properties(obj):
    print(f"   Name:            \"{obj.GetName()}\"")
    print(f"   PartNumber:      \"{obj.GetPartNumber()}\"")

    object_type = obj.GetType()
    print("object_type", object_type)

    if obj.HasSlices(False):
        slice_stack = obj.GetSliceStack()
        show_slice_stack(slice_stack, "   ")

    if obj.GetMetaDataGroup().GetMetaDataCount() > 0:
        show_metadata_information(obj.GetMetaDataGroup())

def show_mesh_object_information(mesh_object):
    print(f"mesh object #{mesh_object.GetResourceID()}:")

    show_object_properties(mesh_object)

    n_vertex_count = mesh_object.GetVertexCount()
    n_triangle_count = mesh_object.GetTriangleCount()
    beam_lattice = mesh_object.BeamLattice()

    print(f"   Vertex count:    {n_vertex_count}")
    print(f"   Triangle count:  {n_triangle_count}")

    n_beam_count = beam_lattice.GetBeamCount()
    if n_beam_count > 0:
        print(f"   Beam count:  {n_beam_count}")
        n_representation_mesh = beam_lattice.GetRepresentation()
        if n_representation_mesh is not None:
            print(f"   |_Representation Mesh ID:  {n_representation_mesh}")

        e_clip_mode, n_clipping_mesh = beam_lattice.GetClipping()
        if e_clip_mode != lib3mf.BeamLatticeClipMode.NoClipMode:
            print(f"   |_Clipping Mesh ID:  {n_clipping_mesh} (mode={int(e_clip_mode)})")

        if beam_lattice.GetBeamSetCount() > 0:
            print(f"   |_BeamSet count:  {beam_lattice.GetBeamSetCount()}")

def show_transform(transform, indent):
    print(f"{indent}Transformation:  [ {transform[0][0]} {transform[1][0]} {transform[2][0]} {transform[3][0]} ]")
    print(f"{indent}                 [ {transform[0][1]} {transform[1][1]} {transform[2][1]} {transform[3][1]} ]")
    print(f"{indent}                 [ {transform[0][2]} {transform[1][2]} {transform[2][2]} {transform[3][2]} ]")

def show_components_object_information(components_object):
    print(f"components object #{components_object.GetResourceID()}:")

    show_object_properties(components_object)
    print(f"   Component count:    {components_object.GetComponentCount()}")

    for n_index in range(components_object.GetComponentCount()):
        component = components_object.GetComponent(n_index)

        print(f"   Component {n_index}:    Object ID:   {component.GetObjectResourceID()}")
        if component.HasTransform():
            show_transform(component.GetTransform(), "                   ")
        else:
            print("                   Transformation:  none")

'''end of helpers'''
# Create a model instance
model = lib3mf.CreateModel()

# Load the .3mf file
reader = model.QueryReader("3mf")
reader.SetStrictModeActive(False)
reader.ReadFromFile(FILE)

for i_warning in range(reader.GetWarningCount()):
    n_error_code, s_warning_message = reader.GetWarning(i_warning)
    print(f"Encountered warning #{n_error_code} : {s_warning_message}")

#show_thumbnail_information(model)
show_metadata_information(model.GetMetaDataGroup())
## slice_stacks
slice_stacks = model.GetSliceStacks()
print("slice stacks",slice_stacks)
while slice_stacks.MoveNext():
    slice_stack = slice_stacks.GetCurrentSliceStack()
    show_slice_stack(slice_stack, "")

## objects
object_iterator = model.GetObjects()
while object_iterator.MoveNext():
    obj = object_iterator.GetCurrentObject()
    print("obj is MeshObject= ", obj.IsMeshObject())
    if obj.IsMeshObject():
        print(model.GetMeshObjectByID(obj.GetResourceID()))
        show_mesh_object_information(model.GetMeshObjectByID(obj.GetResourceID()))
    elif obj.IsComponentsObject():
        show_components_object_information(model.GetComponentsObjectByID(obj.GetResourceID()))
    else:
        print(f"unknown object #{obj.GetResourceID()}:")

## build items
build_item_iterator = model.GetBuildItems()
while build_item_iterator.MoveNext():
    build_item = build_item_iterator.GetCurrent()

    print(f"Build item (Object #{build_item.GetObjectResourceID()}):")

    if build_item.HasObjectTransform():
        show_transform(build_item.GetObjectTransform(), "   ")
    else:
        print("   Transformation:  none")

    print(f"   Part number:     \"{build_item.GetPartNumber()}\"")
    if build_item.GetMetaDataGroup().GetMetaDataCount() > 0:
        show_metadata_information(build_item.GetMetaDataGroup())

print("done")