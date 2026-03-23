import sys
import importlib

def reload_package(package_name):
    modules = {
        name: module
        for name, module in sys.modules.items()
        if name.startswith(package_name)
    }

    # Sort so parents reload before children (important)
    for name in sorted(modules.keys()):
        try:
            importlib.reload(modules[name])
        except Exception as e:
            print(f"Failed to reload {name}: {e}")