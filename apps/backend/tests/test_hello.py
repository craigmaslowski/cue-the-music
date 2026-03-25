"""Hello unit test module."""

from cue_the_music.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello backend"
