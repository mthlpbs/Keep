# import youtube module from parent directory
import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# test file
import utils
import youtube
import main as project


def test_downloader_bypass():
    ytd = youtube.downloader(
        r"https://www.youtube.com/watch?v=_9TgVAYP3XA", bypass=True
    )
    assert hasattr(ytd, "quality") == False
    assert hasattr(ytd, "subtitle") == False
    assert hasattr(ytd, "output") == False
    assert hasattr(ytd, "cookies") == True
    assert hasattr(ytd, "url") == True
    assert ytd.url == r"https://www.youtube.com/watch?v=_9TgVAYP3XA"


def test_downloader():
    ytd = youtube.downloader(
        r"https://www.youtube.com/watch?v=_9TgVAYP3XA",
        quality="720",
        subtitle=["en", "si"],
    )
    assert hasattr(ytd, "subtitle") == True
    assert hasattr(ytd, "output") == True
    assert hasattr(ytd, "cookies") == True
    assert hasattr(ytd, "url") == True
    assert ytd.quality == 720
    assert ytd.subtitle == ["en", "si"]
    assert ytd.url == r"https://www.youtube.com/watch?v=_9TgVAYP3XA"
    assert ytd.output == str(Path.home() / "Downloads")


def test_url():
    with pytest.raises(SystemExit):
        ytd = youtube.downloader(
            r"https://x.com/wonderofscience/status/1997281870434951456"
        )


def test_cookies():
    with pytest.raises(SystemExit):
        ytd = youtube.downloader(
            r"https://www.youtube.com/watch?v=_9TgVAYP3XA",
            cookie="non_existent_cookie.txt",
        )


def test_end():
    with patch("rich.prompt.Prompt.ask", return_value="y"), patch(
        "main.handler"
    ) as mock_handler:
        project.end()
        mock_handler.assert_called_once()

    with patch("rich.prompt.Prompt.ask", return_value="n"), patch(
        "sys.exit"
    ) as mock_exit:
        project.end()
        mock_exit.assert_called_with(0)


def test_project_main():
    with patch("rich.prompt.Prompt.ask", return_value="1"), patch(
        "main.handler"
    ) as mock_handler:
        project.main()
        assert project.intp == 1
        mock_handler.assert_called_once()

    with patch("rich.prompt.Prompt.ask", return_value="0"), patch(
        "main.handler"
    ) as mock_handler:
        project.main()
        assert project.intp == 0
        mock_handler.assert_called_once()


def test_recognizer_url():
    assert (
        utils.recognizer.url("https://www.youtube.com/watch?v=ZVN9LVqAyyo") == "youtube"
    )
    assert utils.recognizer.url("https://vimeo.com/347119375") == "none"
