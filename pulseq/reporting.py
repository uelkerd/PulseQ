# framework/reporting.py

import subprocess


def generate_allure_report():
    """
    Generate an HTML report using Allure.
    Make sure Allure is installed on your system.
    """
    try:
        subprocess.run(
            ["allure", "generate", "allure-results",
                "-o", "allure-report", "--clean"],
            check=True,
        )
        print("Allure report generated successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to generate Allure report:", e)


if __name__ == "__main__":
    generate_allure_report()
