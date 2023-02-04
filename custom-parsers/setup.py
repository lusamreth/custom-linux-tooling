from setuptools import setup

setup(
    name="dunst_controller",
    version="0.1.0",
    py_modules=["dunst_controller"],
    install_requires=["Click", "pulsectl"],
    entry_points={
        "console_scripts": [
            "dunst_controller = dunst_controller:cli",
        ],
    },
)
