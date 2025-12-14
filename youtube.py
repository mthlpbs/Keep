import re
import os
import sys
import json
import time
import utils
import yt_dlp
import pycountry
from shutil import which
from pathlib import Path
from rich.prompt import Prompt
from rich.console import Console
from typing import Optional as optional

invalid_chars = r'<>:"/\|?*'


class downloader:
    """
    YouTube Video Downloader Class.
    """

    def __init__(
        self,
        url: str = None,
        cookie: str = None,
        quality: str = None,
        subtitle: list[str] = None,
        output: str = None,
        bypass: bool = False,
    ):
        """
        Initialize the downloader with the provided parameters.

        By default, checks for a cookie file in the 'cookies' directory if none is provided.

        Args:
            url (str): The YouTube video URL to download.
            cookie (str, optional): Path to a cookie file or supported browser name. Defaults to None. Recommended to use cookies file because cookies extraction from browser is not reliable.
            quality (str, optional): Target video quality in pixels (e.g., "720"). Defaults to None.
            subtitle (list[str], optional): List of language codes for preferred subtitles. Defaults to None.
            output (str, optional): Output directory path for downloaded videos. Defaults to None.
        """
        self.ydl_opts = {
            "remote_components": ["ejs:github"],
            "merge_output_format": "mkv",
            "quiet": True,
            "no_warnings": True,
            "embedthumbnail": True,
            "writethumbnail": True,
            "embedinfojson": True,
            "embedmetadata": True,
            "embedchapters": True,
            "xattrs": True,
            "nodownloadarchive": True,
        }
        if which("ffmpeg") is not None:
            self.ydl_opts.update(
                {
                    "ffmpeg_location": which("ffmpeg"),
                    "postprocessors": [
                        {
                            "key": "EmbedThumbnail",
                            "already_have_thumbnail": False,
                        },
                        {
                            "key": "FFmpegMetadata",
                            "add_metadata": True,
                            "add_chapters": True,
                        },
                        {
                            "key": "FFmpegEmbedSubtitle",
                            "already_have_subtitle": False,
                        },
                    ],
                }
            )
        elif not which("yt-dlp"):
            try:
                console = Console()
                console.print(
                    "\n[bold red]❌ yt-dlp library not found! Please install the required dependencies.[/bold red]\n"
                )
                sys.exit(1)
            except ModuleNotFoundError:
                sys.exit(
                    "\n❌ Rich module not found! Please install the required dependencies.\n"
                )
        self.url = url
        self.cookies = cookie
        if utils.test.check_internet_conn() is True:
            self.info = self.extract_info()
        else:
            console = Console()
            console.print(
                "\n[bold red]❌ No internet connection! Please check your connection and try again.[/bold red]\n"
            )
            sys.exit(1)
        if not bypass:
            self.quality = quality
            self.subtitle = subtitle
            self.output = output

    @property
    def url(self) -> str:
        """
        Returns:
            str: The URL of the YouTube video.
        """
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        """
        Sets the URL of the YouTube video.

        Args:
            url (str): The URL to set.

        Raises:
            exception.LinkError: If the URL is not provided or is invalid.
        """
        try:
            console = Console()
            if not url:
                while True:
                    url = Prompt.ask(
                        "\n[bold bright_blue]Please enter the YouTube video URL you want to download[/bold bright_blue]"
                    )
                    if url:
                        break
                    else:
                        console.print(
                            "\n[bold red]❌ URL cannot be empty! Please enter a valid YouTube video URL.[/bold red]\n"
                        )
            # regex pattern is adapted from https://stackoverflow.com/questions/3717115/regular-expression-for-youtube-links
            if not re.search(
                r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})(?:&[^#\s]*)?$",
                url,
            ):
                raise utils.LinkError()
            self._url = url
            return
        except utils.LinkError as e:
            console.print(
                f"\n[bold red]❌ Error![/bold red] [yellow]{str(e)}[/yellow]\n"
            )
            self.url = None
        except KeyboardInterrupt or UnboundLocalError:
            console.print(
                "\n\n[bold bright_green]Operation cancelled by user.[bold bright_green]Goodbye...! 👋[/bold bright_green]\n"
            )
            sys.exit(1)

    @property
    def cookies(self) -> str:
        """
        Returns:
            str: The path to the cookie file or browser name.
        """
        return self._cookies

    @cookies.setter
    def cookies(self, cookie: str = "") -> None:
        """
        Sets the path to the cookie file or browser name. Defaults to checking for a default cookie file in the 'cookies' directory.

        Args:
            cookie (str): Path to the cookie file or browser name. Browsers supported are:
                - brave
                - chrome
                - chromium
                - edge
                - firefox
                - opera
                - safari
                - vivaldi
                - whale

        Raises:
            exception.FileError: If the cookie file does not exist or is not a .txt file.
        """
        supported_browsers = [
            "brave",
            "chrome",
            "chromium",
            "edge",
            "firefox",
            "opera",
            "safari",
            "vivaldi",
            "whale",
        ]
        if not cookie:
            console = Console()
            cookie_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "cookies/youtube.txt"
            )
            if os.path.exists(cookie_file):
                self._cookies = cookie_file
                self.ydl_opts["cookiefile"] = self._cookies
                return
            else:
                console.print(
                    "\n[bold red]❌ No cookie file provided![/bold red] [yellow]Please create a youtube.txt file in the 'cookies' directory and paste your cookies there. After creating the file, please try again.[/yellow]\n"
                )
                sys.exit(1)
        elif cookie.lower() in supported_browsers:
            self._cookies = cookie.lower()
            self.ydl_opts["cookiesfrombrowser"] = self._cookies
            return

        elif not os.path.exists(cookie) or not os.path.splitext(cookie)[-1] == ".txt":
            console = Console()
            try:
                raise utils.FileError(cookie)
            except utils.FileError as e:
                console.print(
                    f"\n[bold red]❌ File Error![/bold red] [yellow]{str(e)}[/yellow]\n"
                )
                sys.exit(1)
        else:
            self._cookies = cookie
            self.ydl_opts["cookiefile"] = self._cookies
            return

    @property
    def info(self) -> str:
        """
        Returns:
            str: The video information in JSON format.
        """
        return json.dumps(self._info, indent=4)

    @info.setter
    def info(self, info: dict) -> None:
        """
        Sets the video information.

        Args:
            info (dict): The video information to set.
        """
        self._info = info
        return

    def exportInfo(self) -> None:
        """
        Exports the video information to a JSON file.
        """
        from rich.spinner import Spinner
        from rich.live import Live

        file = f"{self._info['title']} - info.json"
        console = Console()
        with Live(
            Spinner(
                "dots",
                text=f"[cyan]Exporting video information to {file}...",
                style="bold cyan",
            ),
            console=console,
            transient=True,
        ):
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self._info, f, indent=4, ensure_ascii=False)

        console.print(
            f"[bold green]✓[/bold green] [green]Information exported successfully to {file}![/green]\n"
        )
        return

    @staticmethod
    def importInfo(path: str) -> dict:
        """
        Imports video information from a JSON file.

        Args:
            path (str): The path to the JSON file.

        Returns:
            dict: The video information.
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract_info(self) -> dict:
        """
        Extracts video information without downloading the video. To use this metthod, use the 'bypass = True' parameter while initializing the downloader class.

        Returns:
            dict: The extracted video information.
        """
        from rich.spinner import Spinner
        from rich.live import Live

        try:
            console = Console()
            ydl_opts = self.ydl_opts.copy()
            ydl_opts = {
                key: value
                for key, value in ydl_opts.items()
                if key
                not in [
                    "embedthumbnail",
                    "writethumbnail",
                    "embedchapters",
                    "embedmetadata",
                    "embedinfojson",
                    "xattr",
                    "merge_output_format",
                ]
            }
            ydl_opts["format"] = "bestvideo+bestaudio/best"
            with Live(
                Spinner(
                    "dots",
                    text="[cyan]Extracting video information...",
                    style="bold cyan",
                ),
                console=console,
                transient=True,
            ):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    data = ydl.extract_info(self.url, download=False)
            console.print(
                "[bold cyan]✓[/bold cyan] [cyan]Video information extracted successfully![/cyan]"
            )
            for char in invalid_chars:
                data["title"] = data["title"].replace(char, "-")
            return data
        except yt_dlp.utils.DownloadError as e:
            sys.exit(1)

        except yt_dlp.utils.ExtractorError as e:
            sys.exit(1)
        except KeyboardInterrupt or UnboundLocalError:
            console.print(
                "\n\n[bold bright_green]Operation cancelled by user.[bold bright_green]Goodbye...! 👋[/bold bright_green]\n"
            )
            sys.exit(1)

    @property
    def subtitle(self) -> list[str]:
        """
        Returns the list of subtitle languages.

        Returns:
            list[str]: The list of subtitle languages.
        """
        return self._subtitle

    @subtitle.setter
    def subtitle(self, subtitle: list[str]) -> None:
        try:
            """
            Sets the list of subtitle languages.

            Args:
                subtitle (list[str]): The list of subtitle languages to set.
            """
            if not subtitle:
                choice = Prompt.ask(
                    "\n[bold bright_blue]Do you want to download subtitles? [/bold bright_blue]",
                    choices=["y", "n"],
                )
                if choice == "n":
                    return
                else:
                    console = Console()
                    console.print(
                        "\n[bold bright_blue]Available subtitles for this video:[/bold bright_blue]\n"
                    )
                    langCodes = list(self._info["subtitles"].keys()) + list(
                        self._info["automatic_captions"].keys()
                    )
                    langCodes = sorted(list(set(langCodes)))
                    for i, code in enumerate(langCodes, start=1):
                        language = pycountry.languages.get(alpha_2=code.upper())
                        language_name = language.name if language else code.upper()
                        console.print(
                            f"    [medium_turquoise]{i}.[/medium_turquoise] [white]{code} - {language_name}[/white]"
                        )
                    subtitle_input = Prompt.ask(
                        "\nEnter the language codes of the subtitles you want to download (separated by commas):"
                    )
                    subtitle = [
                        lang.strip().lower()
                        for lang in subtitle_input.split(",")
                        if lang.strip()
                    ]
                    self.ydl_opts["writesubtitles"] = True
                    self.ydl_opts["writeautomaticsub"] = True
                    self.ydl_opts["subtitlesformat"] = "srt"
                    self.ydl_opts["embedsubtitles"] = True
                    self._subtitle = [lang.lower() for lang in subtitle]
                    self.ydl_opts["subtitleslangs"] = self._subtitle
                    console.clear()
                    return
            elif type(subtitle) is not list:
                console = Console()
                console.print(
                    "\n[bold red]❌ Subtitles must be provided as a list of language codes![/bold red]\n"
                )
                sys.exit(1)
            elif not self._info["subtitles"] and not self._info["automatic_captions"]:
                console = Console()
                console.print(
                    "\n[bold red]❌ No subtitles found for this video![/bold red]\n"
                )
                return
            elif all(
                pycountry.languages.get(alpha_2=lang.upper()) for lang in subtitle
            ):
                self.ydl_opts["writesubtitles"] = True
                self.ydl_opts["writeautomaticsub"] = True
                self.ydl_opts["subtitlesformat"] = "srt"
                self.ydl_opts["embedsubtitles"] = True
                self._subtitle = [lang.lower() for lang in subtitle]
                self.ydl_opts["subtitleslangs"] = self._subtitle
                return
            else:
                console = Console()
                console.print(
                    "\n[bold red]❌ Invalid language code(s) provided for subtitles![/bold red]\n"
                )
                return
        except KeyboardInterrupt or UnboundLocalError:
            console.print(
                "\n\n[bold bright_green]Operation cancelled by user.[bold bright_green]Goodbye...! 👋[/bold bright_green]\n"
            )
            sys.exit(1)

    @property
    def quality(self) -> str:
        """
        Returns the selected video quality.

        Returns:
            str: The selected video quality.
        """
        return self._quality

    @quality.setter
    def quality(self, quality: optional[str] = None) -> None:
        """
        Sets the selected video quality.

        Args:
            quality (str, optional): The selected video quality to set. Defaults to None.
        """
        if quality is not None and type(quality) is not str:
            console = Console()
            console.print(
                "\n[bold red]❌ Quality must be provided as a string![/bold red]\n"
            )
            sys.exit(1)
        qualities = []
        for format in self._info["formats"]:
            try:
                if format["video_ext"] and format["height"] is not None and int(format["height"]) > 180:
                    qualities.append(int(format["height"]))
            except KeyError:
                continue
        qualities = sorted(list(set(qualities)))
        if not quality:
            wait_seconds = 2
            while True:
                try:
                    console = Console()
                    console.print(
                        "\n[bold bright_blue]Select the quality you want to download:[/bold bright_blue]\n"
                    )
                    for i, quality in enumerate(qualities, start=1):
                        console.print(
                            f"    [medium_turquoise]{i}.[/medium_turquoise] [white]{quality}p[/white]"
                        )
                    self._quality = qualities[
                        int(
                            Prompt.ask(
                                f"\nChoice [bold bright_magenta][1/2/.../{len(qualities)}][/bold bright_magenta]"
                            )
                        )
                        - 1
                    ]
                    self.ydl_opts["format"] = (
                        f"bestvideo[height={self._quality}]+bestaudio/bestvideo[height<={self._quality}]+bestaudio/best[height={self._quality}]/best"
                    )
                    console.clear()
                    break
                except IndexError:
                    console.print(
                        "\n[bold red]🚨 Invalid choice![/bold red] [yellow]Please enter a number corresponding to one of the browsers listed.[/yellow]"
                    )
                    time.sleep(wait_seconds)
                    console.clear()

                except ValueError:
                    console.print(
                        "\n[bold red]❌ Invalid input![/bold red] [yellow]Please enter a valid whole number (e.g., 1, 2, 3).[/yellow]"
                    )
                    time.sleep(wait_seconds)
                    console.clear()

                except KeyboardInterrupt or UnboundLocalError:
                    console.print(
                        "\n\n[bold bright_green]Operation cancelled by user.[bold bright_green]Goodbye...! 👋[/bold bright_green]\n"
                    )
                    sys.exit(1)

        else:
            if int(quality) in qualities:
                self._quality = int(quality)
                self.ydl_opts["format"] = (
                    f"bestvideo[height<={self._quality}]+bestaudio"
                )
            else:
                console = Console()
                console.print(
                    "\n[bold red]❌ The specified quality is not available for this video![/bold red]\n"
                )
                sys.exit(1)

    @property
    def output(self) -> str:
        """
        Returns the output directory.

        Returns:
            str: The output directory.
        """
        return self._output

    @output.setter
    def output(self, output: str = None) -> None:
        """
        Sets the output directory.

        Args:
            output (str, optional): The output directory to set. Defaults to None.
        """
        if output and os.path.isdir(output):
            self._output = output
        else:
            self._output = str(Path.home() / "Downloads")
        self.ydl_opts["outtmpl"] = os.path.join(self._output, "%(title)s.%(ext)s")
        return

    def download(self) -> None:
        """
        Downloads the video with a progress bar.
        """
        from rich.progress import Progress, BarColumn

        title = self._info["title"][:50]
        try:
            console = Console()
            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Downloading '{title}' in {self._quality}p...[/cyan]",
                    total=100,
                )

                def progress_hook(d):
                    if d["status"] == "downloading":
                        downloaded_bytes = d.get("downloaded_bytes", 0)
                        total_bytes = d.get("total_bytes") or d.get(
                            "total_bytes_estimate"
                        )
                        if total_bytes:
                            percentage = downloaded_bytes / total_bytes * 100
                            progress.update(task, completed=percentage)
                    elif d["status"] == "finished":
                        progress.update(task, completed=100)

                self.ydl_opts["progress_hooks"] = [progress_hook]

                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    ydl.download([self.url])

            console.print(
                f"\n[bold green]✓[/bold green] [green]Download completed successfully![/green]\n"
            )
        except yt_dlp.utils.DownloadError as e:
            sys.exit(1)
        except KeyboardInterrupt or UnboundLocalError:
            console.print(
                "\n\n[bold bright_green]Operation cancelled by user.[bold bright_green]Goodbye...! 👋[/bold bright_green]\n"
            )
            sys.exit(1)


def main(url=None, cookie=None, quality=None, subtitle=None, output=None):
    dd = downloader(
        url=url,
        cookie=cookie,
        quality=quality,
        subtitle=subtitle,
        output=output,
    )
    dd.download()
    return


if __name__ == "__main__":
    main()
