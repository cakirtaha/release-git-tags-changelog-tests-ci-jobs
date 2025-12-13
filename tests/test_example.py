"""Example tests to verify test setup works."""

"""Hello"""


def test_basic_math():
    """Test that basic math works."""
    assert 2 + 2 == 4
    assert 5 - 3 == 2
    assert 3 * 4 == 12


def test_strings():
    """Test that string operations work."""
    assert "hello".upper() == "HELLO"
    assert "WORLD".lower() == "world"
    assert "test".startswith("te")


def test_lists():
    """Test that list operations work."""
    items = [1, 2, 3]
    assert len(items) == 3
    assert 2 in items
    assert items[0] == 1
