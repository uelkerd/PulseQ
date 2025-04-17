# tests/test_visual_comparison.py

import pytest
from selenium.webdriver.common.by import By

from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.visual_utils import VisualTester
from pulseq.utilities.wait_utils import WaitUtils


@pytest.fixture
def driver():
    """Initialize the WebDriver."""
    driver = initialize_driver(headless=True)
    yield driver
    quit_driver(driver)


@pytest.fixture
def visual_tester():
    """Initialize the visual tester."""
    return VisualTester()


def test_homepage_visual_comparison(driver, visual_tester):
    """
    Test visual comparison of the homepage.

    This test:
    1. Takes a screenshot of the homepage
    2. Compares it with a baseline
    3. Creates a new baseline if none exists
    """
    # Navigate to the homepage
    driver.get("https://reqres.in/")

    # Wait for the page to load
    wait_utils = WaitUtils(driver)
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, "body"))

    # Take screenshot
    screenshot_path = visual_tester.take_screenshot(driver, "homepage")

    # Try to compare with baseline
    baseline_path = visual_tester.screenshots_dir / "baselines" / "homepage.png"

    if not baseline_path.exists():
        # Create baseline if it doesn't exist
        baseline_path = visual_tester.create_baseline(screenshot_path, "homepage")
        pytest.skip("Baseline created. Run test again to perform comparison.")

    # Compare screenshots
    matches, similarity, diff_path = visual_tester.compare_screenshots(
        screenshot_path, str(baseline_path), threshold=0.95
    )

    # Assert screenshots match
    assert matches, (
        f"Screenshots differ (similarity: {similarity:.2f}). "
        f"See diff image: {diff_path}"
    )


def test_user_list_visual_comparison(driver, visual_tester):
    """
    Test visual comparison of the user list page.

    This test:
    1. Navigates to the user list page
    2. Takes a screenshot
    3. Compares it with a baseline
    """
    # Navigate to the user list page
    driver.get("https://reqres.in/#/users")

    # Wait for the page to load
    wait_utils = WaitUtils(driver)
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, ".user-list"))

    # Take screenshot
    screenshot_path = visual_tester.take_screenshot(driver, "user_list")

    # Try to compare with baseline
    baseline_path = visual_tester.screenshots_dir / "baselines" / "user_list.png"

    if not baseline_path.exists():
        # Create baseline if it doesn't exist
        baseline_path = visual_tester.create_baseline(screenshot_path, "user_list")
        pytest.skip("Baseline created. Run test again to perform comparison.")

    # Compare screenshots
    matches, similarity, diff_path = visual_tester.compare_screenshots(
        screenshot_path, str(baseline_path), threshold=0.95
    )

    # Assert screenshots match
    assert matches, (
        f"Screenshots differ (similarity: {similarity:.2f}). "
        f"See diff image: {diff_path}"
    )
