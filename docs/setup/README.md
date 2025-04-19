# Environment Setup Guide

This guide provides detailed instructions for setting up the PulseQ framework on different operating systems.

## Table of Contents

- [Windows Setup](#windows-setup)
- [macOS Setup](#macos-setup)
- [Linux Setup](#linux-setup)
- [Docker Setup](#docker-setup)
- [Cloud Setup](#cloud-setup)

## Windows Setup

### Prerequisites

- Windows 10 or later
- Python 3.8 or higher
- Git
- Chrome or Firefox browser
- Java Runtime Environment (for Allure reporting)

### Installation Steps

1. **Install Python**

   ```powershell
   # Download and install Python from https://www.python.org/downloads/
   # Make sure to check "Add Python to PATH" during installation
   ```

2. **Install Git**

   ```powershell
   # Download and install Git from https://git-scm.com/download/win
   ```

3. **Clone the Repository**

   ```powershell
   git clone https://github.com/uelkerd/PulseQ.git
   cd PulseQ
   ```

4. **Create Virtual Environment**

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

5. **Install Dependencies**

   ```powershell
   pip install -e .
   ```

6. **Install Browser Drivers**

   ```powershell
   # For Chrome
   pip install webdriver-manager
   python -m webdriver_manager install chrome

   # For Firefox
   python -m webdriver_manager install firefox
   ```

## macOS Setup

### Prerequisites

- macOS 10.15 or later
- Python 3.8 or higher
- Git
- Chrome or Firefox browser
- Java Runtime Environment (for Allure reporting)

### Installation Steps

1. **Install Homebrew**

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python and Git**

   ```bash
   brew install python git
   ```

3. **Clone the Repository**

   ```bash
   git clone https://github.com/uelkerd/PulseQ.git
   cd PulseQ
   ```

4. **Create Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies**

   ```bash
   pip install -e .
   ```

6. **Install Browser Drivers**

   ```bash
   # For Chrome
   pip install webdriver-manager
   python -m webdriver_manager install chrome

   # For Firefox
   python -m webdriver_manager install firefox
   ```

## Linux Setup

### Prerequisites

- Ubuntu 20.04 or later (or equivalent)
- Python 3.8 or higher
- Git
- Chrome or Firefox browser
- Java Runtime Environment (for Allure reporting)

### Installation Steps

1. **Install System Dependencies**

   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv git
   ```

2. **Clone the Repository**

   ```bash
   git clone https://github.com/uelkerd/PulseQ.git
   cd PulseQ
   ```

3. **Create Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**

   ```bash
   pip install -e .
   ```

5. **Install Browser Drivers**

   ```bash
   # For Chrome
   pip install webdriver-manager
   python -m webdriver_manager install chrome

   # For Firefox
   python -m webdriver_manager install firefox
   ```

## Docker Setup

### Prerequisites

- Docker
- Docker Compose

### Installation Steps

1. **Build the Docker Image**

   ```bash
   docker build -t pulseq .
   ```

2. **Run the Container**

   ```bash
   docker-compose up -d
   ```

3. **Access the Framework**
   ```bash
   # The framework will be available at http://localhost:8080
   ```

## Cloud Setup

### AWS Setup

1. **Create EC2 Instance**

   ```bash
   # Use the provided CloudFormation template
   aws cloudformation create-stack --stack-name pulseq --template-body file://cloudformation/template.yaml
   ```

2. **Configure Security Groups**

   ```bash
   # Allow necessary ports (8080, 8081-8083)
   ```

3. **Access the Framework**
   ```bash
   # The framework will be available at http://<instance-ip>:8080
   ```

### Azure Setup

1. **Create VM**

   ```bash
   # Use the provided ARM template
   az deployment group create --resource-group myResourceGroup --template-file azure/template.json
   ```

2. **Configure Network Security**

   ```bash
   # Allow necessary ports (8080, 8081-8083)
   ```

3. **Access the Framework**
   ```bash
   # The framework will be available at http://<vm-ip>:8080
   ```

## Verification

After setup, verify your installation by running:

```bash
pytest tests/verify_installation.py
```

## Troubleshooting

If you encounter any issues during setup, refer to the [Troubleshooting Guide](../troubleshooting.md).

## Next Steps

- [Quick Start Guide](../quickstart.md)
- [Advanced Features Tutorial](../tutorials/advanced_features.ipynb)
- [API Documentation](../api/README.md)
