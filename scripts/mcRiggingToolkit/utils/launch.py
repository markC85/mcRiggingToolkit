from mcRiggingToolkit.utils.reload import reload_package

def run():
    reload_package("mcRiggingToolkit")

    from mcRiggingToolkit.ui import ui_main
    ui_main.show_ui()