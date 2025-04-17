# pulseq/utilities/visual_utils.py

import os
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver

from pulseq.utilities.logger import setup_logger

logger = setup_logger("visual_utils")


class VisualTester:
    """Utility class for visual testing and screenshot comparison."""

    def __init__(self, screenshots_dir: str = "screenshots"):
        """
        Initialize the visual tester.

        Args:
            screenshots_dir: Directory to store screenshots
        """
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"Initialized VisualTester with screenshots directory: {screenshots_dir}"
        )

    def take_screenshot(self, driver: WebDriver, name: str) -> str:
        """
        Take a screenshot and save it to the screenshots directory.

        Args:
            driver: WebDriver instance
            name: Name for the screenshot file

        Returns:
            str: Path to the saved screenshot
        """
        screenshot_path = self.screenshots_dir / f"{name}.png"
        driver.save_screenshot(str(screenshot_path))
        logger.info(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)

    def compare_screenshots(
        self, current_screenshot: str, baseline_screenshot: str, threshold: float = 0.95
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Compare two screenshots and return similarity metrics.

        Args:
            current_screenshot: Path to current screenshot
            baseline_screenshot: Path to baseline screenshot
            threshold: Similarity threshold (0-1)

        Returns:
            Tuple[bool, float, Optional[str]]:
                - Whether screenshots match (bool)
                - Similarity score (float)
                - Path to diff image if mismatch (Optional[str])
        """
        # Read images
        current = cv2.imread(current_screenshot)
        baseline = cv2.imread(baseline_screenshot)

        if current is None or baseline is None:
            logger.error("Failed to read one or both screenshots")
            return False, 0.0, None

        # Resize if dimensions don't match
        if current.shape != baseline.shape:
            baseline = cv2.resize(baseline, (current.shape[1], current.shape[0]))

        # Convert to grayscale
        current_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
        baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)

        # Calculate structural similarity
        from skimage.metrics import structural_similarity

        score, diff = structural_similarity(current_gray, baseline_gray, full=True)

        # Convert diff to uint8
        diff = (diff * 255).astype("uint8")

        # Create diff image if similarity is below threshold
        diff_path = None
        if score < threshold:
            diff_path = str(
                Path(current_screenshot).with_name(
                    f"{Path(current_screenshot).stem}_diff.png"
                )
            )
            cv2.imwrite(diff_path, diff)
            logger.warning(
                f"Screenshots differ (similarity: {score:.2f}). "
                f"Diff image saved: {diff_path}"
            )

        return score >= threshold, score, diff_path

    def create_baseline(self, screenshot: str, name: str) -> str:
        """
        Create a baseline screenshot by copying the current screenshot.

        Args:
            screenshot: Path to current screenshot
            name: Name for the baseline

        Returns:
            str: Path to the baseline screenshot
        """
        baseline_path = self.screenshots_dir / "baselines" / f"{name}.png"
        baseline_path.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(screenshot) as img:
            img.save(baseline_path)

        logger.info(f"Baseline created: {baseline_path}")
        return str(baseline_path)
