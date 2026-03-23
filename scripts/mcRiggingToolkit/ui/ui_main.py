from maya import cmds, OpenMayaUI
import maya.api.OpenMaya as om
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QPalette
from shiboken6 import wrapInstance
from mcRiggingToolkit.core.rig_template import create_rig_template
import logging


LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")

def get_maya_main_window() -> None:
    """
    Attach the QTWidgets to the maya main window
    so that it will act like it belongs to maya
    to help prevent bugs and crashes
    """
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

def show_ui() -> None:
    """
    Buld the UI and delete it if its there
    """
    global simple_button_ui

    try:
        simple_button_ui.close()
        simple_button_ui.deleteLater()
    except:
        pass

    simple_button_ui = RiggingToolsUI()
    simple_button_ui.show()

class RiggingToolsUI(QtWidgets.QDialog):
    """
    Bundle of rigging tools
    """

    def __init__(self, parent=None) -> None:
        if parent is None:
            parent = get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle("mc Rigging Toolkit")
        self.setMinimumWidth(300)

        self.build_ui()
        self.create_connections()

        self.ctrl_color = None

    def build_ui(self) -> None:
        """
        UI fields and layout
        """
        #######################################
        ## Build controllers
        #######################################
        self.ctrl_custom_name_checkbox = QtWidgets.QCheckBox("Create Custom Name")
        self.ctrl_name_label = QtWidgets.QLabel("Create Animation Controller:")
        self.ctrl_name_field = QtWidgets.QLineEdit()
        self.ctrl_name_field.setPlaceholderText("Enter Controle name")
        self.ctrl_name_field.hide()
        self.color_label = QtWidgets.QLabel("Set Controller Color:")
        # set color buttons
        self.red_btn = QtWidgets.QPushButton()
        self.red_btn.setStyleSheet("background-color: red;")
        self.blue_btn = QtWidgets.QPushButton()
        self.blue_btn.setStyleSheet("background-color: blue;")
        self.yellow_btn = QtWidgets.QPushButton()
        self.yellow_btn.setStyleSheet("background-color: yellow;")
        self.ctrl_color_btn = QtWidgets.QPushButton("Custom")
        self.ctrl_create_btn = QtWidgets.QPushButton("Create Animation Control")
        self.color_picked_btn = QtWidgets.QPushButton()
        self.color_picked_btn.setFixedSize(140, 30)
        self.color_picked_btn.setEnabled(False)
        self.color_picked_btn.setStyleSheet(
            "background-color: gray; border: 1px solid black;"
        )

        #######################################
        ## Build rig template group
        #######################################
        self.rig_temp_label = QtWidgets.QLabel("Create Rig Groups:")
        self.rig_temp_name_field = QtWidgets.QLineEdit()
        self.rig_temp_name_field.setPlaceholderText("Rig Name")
        self.rig_temp_create_btn = QtWidgets.QPushButton("Create Rig Template Group")

        #######################################
        ## Layout
        #######################################
        main_layout = QtWidgets.QVBoxLayout(self)

        # Build controllers layout
        main_layout.addWidget(self.ctrl_color_btn)
        main_layout.addWidget(self.ctrl_name_label)
        main_layout.addWidget(self.ctrl_custom_name_checkbox)
        main_layout.addWidget(self.ctrl_name_field)
        color_picked_layout = QtWidgets.QHBoxLayout()
        color_picked_layout.addWidget(self.color_label)
        color_picked_layout.addWidget(
            self.color_picked_btn, alignment=QtCore.Qt.AlignLeft
        )
        main_layout.addLayout(color_picked_layout)

        # Horizontal layout for color buttons
        palette_layout = QtWidgets.QHBoxLayout()
        palette_layout.addWidget(self.red_btn)
        palette_layout.addWidget(self.blue_btn)
        palette_layout.addWidget(self.yellow_btn)
        palette_layout.addWidget(self.ctrl_color_btn)
        main_layout.addLayout(palette_layout)
        main_layout.addWidget(self.ctrl_create_btn)

        # rig template group layout
        main_layout.addWidget(self.rig_temp_label)
        main_layout.addWidget(self.rig_temp_name_field)
        main_layout.addWidget(self.rig_temp_create_btn)

    def set_ctrl_collor(self, color_value: int) -> None:
        """
        This will set the controller color if its selected
        when you are changing the UI controller color pallet

        Args:
            color_value = This is the value to set the color to
                            1 = Red
                            2 = Blue
                            3 = Yellow
                            4 = Custom color
        """
        if color_value == 1:
            self.set_color(QtGui.QColor("red"))
        elif color_value == 2:
            self.set_color(QtGui.QColor("blue"))
        elif color_value == 3:
            self.set_color(QtGui.QColor("yellow"))
        elif color_value == 4:
            self.get_picker_color()

        selection_list = cmds.ls(selection = True, type = "transform")
        for item in selection_list:
            self.set_controller_color(item)

    def create_connections(self) -> None:
        """
        Connect UI button logic
        """
        self.ctrl_create_btn.clicked.connect(self.create_blank_controller)
        self.red_btn.clicked.connect(lambda: self.set_ctrl_collor(1))
        self.blue_btn.clicked.connect(lambda: self.set_ctrl_collor(2))
        self.yellow_btn.clicked.connect(lambda: self.set_ctrl_collor(3))
        self.ctrl_color_btn.clicked.connect(lambda: self.set_ctrl_collor(4))
        self.ctrl_custom_name_checkbox.toggled.connect(
            lambda checked: self.ctrl_name_field.setVisible(checked)
        )
        self.rig_temp_create_btn.clicked.connect(
            lambda: create_rig_template(self.rig_temp_name_field.text().strip())
        )

    def set_color(self, color: QtGui.QColor) -> None:
        """
        Store and preview the color in the UI

        Args:
            color (QtGui.QColor): This is the color for the controller
        """
        self.ctrl_color = (color.redF(), color.greenF(), color.blueF())
        LOG.debug(f"Stored button color:{self.ctrl_color}")

        self.color_picked_btn.setStyleSheet(f"background-color: {color.name()}")

    def get_picker_color(self) -> None:
        """
        Get the UI picker color
        """
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.set_color(color)

    def match_objects_space(self, target_object: str, move_object: str) -> None:
        """
        Match world space of move_object to target_object

        Args:
            target_object (str): this is the object you want to match to
                                 in world space
            move_object (str): this is the object you will be moving
        """
        # get target_object position
        sel = om.MGlobal.getSelectionListByName(target_object)
        dag_path = sel.getDagPath(0)
        fn_transform = om.MFnTransform(dag_path)
        pos = fn_transform.translation(om.MSpace.kWorld)

        # get target_object DAG path
        target_sel = om.MGlobal.getSelectionListByName(move_object)
        target_dag = target_sel.getDagPath(0)
        fn_target = om.MFnTransform(target_dag)

        # Move move_object to target_object
        fn_target.setTranslation(pos, om.MSpace.kWorld)

    def get_selected_object_name(self) -> None:
        """
        Lazily iterate selected DAG objects and yield long names
        """
        sel = om.MGlobal.getActiveSelectionList()

        for i in range(sel.length()):
            try:
                dag = sel.getDagPath(i)
                yield dag.fullPathName()
            except RuntimeError:  # Non-DAG items (shaders, etc.)
                continue

    def unique_ctrl_name(self, base_name: str) -> str:
        """
        Return a unique controller name based on a base_name.
        Adds _01, _02, ... if the base_name already exists.

        Args:
            base_name (str): this is the base name

        Returns:
            name (str): new name created
        """
        name = f"{base_name}_ctrl"
        if not cmds.objExists(name):
            return name

        i = 1
        while True:
            name = f"{base_name}_{i:02d}_ctrl"  # 2-digit suffix like _01, _02
            if not cmds.objExists(name):
                return name
            i += 1

    def create_curve_offset_group(self, controller_name: str) -> None:
        """
        Build the curve and offset group for the controller

        Args:
            controller_name (str): the name of the controller
        """
        short_controller_name = controller_name.split("|")[-1]
        short_controller_name = self.unique_ctrl_name(short_controller_name)
        controller = cmds.circle(name=short_controller_name)
        offset_group = cmds.group(controller, name=f"{short_controller_name}_offset")

        if self.ctrl_custom_name_checkbox.isChecked() is False:
            self.match_objects_space(controller_name, offset_group)

        self.set_controller_color(controller)

    def set_controller_color(self, controller: str) -> None:
        """
        Set the controller color

        Args:
            ctronller (str): this is the name of the controller
        """
        color = self.color_picked_btn.palette().color(QPalette.Button)
        r = color.red()
        g = color.green()
        b = color.blue()

        for shape in cmds.listRelatives(controller, type="nurbsCurve", fullPath=True):
            cmds.setAttr(shape + ".overrideEnabled", 1)
            cmds.setAttr(shape + ".overrideRGBColors", 1)
            cmds.setAttr(shape + ".overrideColorRGB", r/255.0, g/255.0, b/255.0)

    def create_blank_controller(self) -> None:
        """
        Create a animation controller
        """
        orig_sel = om.MGlobal.getActiveSelectionList()  # get origional selection
        if self.ctrl_custom_name_checkbox.isChecked():
            button_name = self.ctrl_name_field.text().strip()
            if not button_name:
                LOG.warning("Button Controler name cannot be empty.")
                return

            self.create_curve_offset_group(button_name)
        else:
            print(self.get_selected_object_name())
            for obj in self.get_selected_object_name():
                self.create_curve_offset_group(obj)

        om.MGlobal.setActiveSelectionList(orig_sel) # restore selection

        LOG.info("Finished creating ctrls")