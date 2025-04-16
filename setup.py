from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="web-test-automation-framework",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A modular test automation framework for web applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/test-automation-framework",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/test-automation-framework/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.1.0",
        "pytest>=7.0.0",
        "allure-pytest>=2.9.0",
        "requests>=2.27.0",
        "python-dotenv>=0.19.0",
        "webdriver-manager>=3.5.0",
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
            "web-test=framework.core:main",
        ],
    },
)
