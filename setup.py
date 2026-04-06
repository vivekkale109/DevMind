from setuptools import setup, find_packages

setup(
    name="devmind",
    version="0.1.0",
    description="Terminal-first coding behavior analyzer",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # watchdog is optional — we fall back to polling without it
        # "watchdog>=3.0",
    ],
    extras_require={
        "fast": ["watchdog>=3.0"],
    },
    entry_points={
        "console_scripts": [
            "devmind=devmind.cli:main",
        ],
    },
)
