import maya.api.OpenMaya as om
from maya import cmds
import re


def selected_vertices_center() -> None:
    """
    This will get the center point of vertex
    that you have selected
    """
    sel = om.MGlobal.getActiveSelectionList()

    if sel.length() == 0:
        raise RuntimeError("We did not find anything selected.")

    points = []

    for i in range(sel.length()):
        dag_path, component = sel.getComponent(i)

        # We only care about mesh vertices
        if component.apiType() != om.MFn.kMeshVertComponent:
            continue

        mesh_fn = om.MFnMesh(dag_path)
        comp_fn = om.MFnSingleIndexedComponent(component)

        for vtx_id in comp_fn.getElements():
            pt = mesh_fn.getPoint(vtx_id, om.MSpace.kWorld)
            points.append(pt)

    if not points:
        raise RuntimeError("No mesh vertices selected currently.")

    # Average all points
    center = om.MPoint()
    for p in points:
        center += p

    center /= len(points)

    return center


def create_joint(name: str = "new", sufix: str = "jnt", position: list = []) -> str:
    """
    This will create a joint in maya

    Args:
        position (list): this is the of positoin to build the joint at specifically
                         it should come in a list [x,y,z] format
        name (str): this is the name of the joint
        sufix (str): this ist he suffix to use for the joint default is 'jnt'

    Returns:
        joint_created (str): this is the name of the joint that is created
    """
    # look for duplicate joint names and auto
    # number them up so all joint names are unique
    find_dup_joints = cmds.ls(name, type="joint")
    if find_dup_joints:
        joint_name = name.split(sufix)[0]
        joint_name = f"{name}{value:03d}_{sufix}"
    else:
        joint_name = name + "_" + sufix

    joint_created = cmds.joint(name=joint_name)

    if position:
        cmds.move(position[0], position[1], position[2], joint_created)

    return joint_created


def create_joint_at_cetered() -> None:
    """
    This will create a joint at the centroid of multiple vertex
    """
    center_point = selected_vertices_center()
    create_joint('test','jnt',list(center_point))