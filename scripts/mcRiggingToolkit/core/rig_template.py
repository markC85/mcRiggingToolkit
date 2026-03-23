from maya import cmds
import logging


LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")

def create_rig_template(rig_name: str) -> None:
    """
    Create the groups for a rig template

    Args:
        rig_name (str): The name of the rig
    """
    if not rig_name:
        LOG.warning("No rig name has been specified.")
        return

    prx_group = cmds.group(empty=True, name="prx_grp", world=True)
    rnd_group = cmds.group(empty=True, name="render_grp", world=True)
    geo_group = cmds.group([prx_group, rnd_group], name="geo_grp", world=True)
    anim_group = cmds.group(empty=True, name="anim_grp", world=True)
    export_group = cmds.group(empty=True, name="export_grp", world=True)
    joint_group = cmds.group([anim_group, export_group], name="jnt_grp", world=True)
    ctrl_group = cmds.group(empty=True, name="ctrl_grp", world=True)
    cmds.group([geo_group, joint_group, ctrl_group], name=rig_name)