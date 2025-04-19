from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pulseq",
    version="0.1.0",
    author="PulseQ Team",
    author_email="team@pulseq.io",
    description="Load Balancer Testing Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pulseq/pulseq",
    project_urls={
        "Bug Tracker": "https://github.com/pulseq/pulseq/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "jsonschema>=4.0.0",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "pytest-cov",
        ],
        "image": [
            "Pillow",
            "numpy",
            "scikit-image",
        ],
        "ocr": [
            "pytesseract",
            "Pillow",
        ],
    },
    entry_points={
        "console_scripts": [
            "pulseq=pulseq.cli.config_cli:cli",
        ],
    },
)
