# framework/utilities/assertions.py

def assert_element_present(element, message="Expected element not found"):
    """Asserts that an element is present on the page."""
    assert element is not None, message

def assert_text_equal(actual, expected, message="Text does not match"):
    """Asserts that text strings are equal."""
    assert actual == expected, f"{message}. Expected: {expected}, Got: {actual}"
