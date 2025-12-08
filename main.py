from rich.prompt import Prompt
from rich.console import Console
from rich.align import Align
import youtube
import sys
import os
import argparse
import utils

intp = int()
sources = ["youtube"]
quality = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]


def handler(
    url: str = None, quality: str = None, subtitle: list[str] = None, output: str = None
) -> None:
    """
    Handles user input and calls the appropriate downloader based on the input.

    Args:
        url (str, optional): The video URL. Defaults to None.
        quality (str, optional): The desired video quality. Defaults to None.
        subtitle (list[str], optional): List of subtitle languages. Defaults to None.
        output (str, optional): The output directory. Defaults to None.
    """
    try:
        match intp:
            case 1:
                youtube.main(url=url, quality=quality, subtitle=subtitle, output=output)
            case 0:
                console = Console()
                console.print("\n[red]Exiting...[/red]\n")
                sys.exit(0)
            case _:
                console = Console()
                console.print("\n[red]Invalid choice! Please try again.[/red]\n")
                main()
        end()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/red]\n")
        sys.exit(0)


def end() -> None:
    """
    Handles end of a process
    """
    try:
        console = Console()
        choice = Prompt.ask(
            "\n[bold bright_blue]Do you want to download again? [/bold bright_blue]",
            choices=["y", "n"],
        )
        if choice == "y":
            console.clear()
            handler()
        else:
            console = Console()
            console.print("\n[bold bright_green]Goodbye...! 👋[/bold bright_green]\n")
            sys.exit(0)
    except KeyboardInterrupt or UnboundLocalError:
        console.print("\n[red]Exiting...[/red]\n")
        sys.exit(0)


def main():
    global intp
    try:
        parser = argparse.ArgumentParser(
            description="Keep ♾️  Videos 🌝 - A simple video downloader."
        )
        parser.add_argument(
            "--platform",
            "-p",
            type=str,
            metavar="site",
            help="Specify the video site name (e.g., youtube)\n Supported sources: youtube",
            choices=sources,
        )
        parser.add_argument(
            "--quality",
            "-q",
            type=str,
            metavar="quality",
            help="Specify the video quality (e.g., 720p)",
            choices=quality,
        )
        parser.add_argument(
            "--subtitle",
            "-s",
            type=str,
            metavar="language codes",
            help="Specify subtitle languages. (For more language codes, separate each language code with commas) (e.g., en, si, kr)",
        )
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            metavar="output",
            help="Specify the output directory",
        )
        parser.add_argument("url", nargs="?", help="Video URL")
        args = parser.parse_args()
        if args.quality:
            args.quality = args.quality.replace("p", "")
        if args.subtitle:
            args.subtitle = [
                code.lower() for code in args.subtitle.replace(" ", "").split(",")
            ]
        if args.output and os.path.isdir(args.output) is False:
            console = Console()
            console.print(f"\n[red]{args.output} is not a valid directory.[/red]\n")
            sys.exit(0)
        if not args.platform and args.url:
            site = utils.recognizer.url(args.url)
            if site in sources:
                intp = sources.index(site) + 1
                handler(
                    url=args.url,
                    quality=args.quality,
                    subtitle=args.subtitle,
                    output=args.output,
                )
            else:
                console = Console()
                console.print(
                    f"\n[red]The provided URL is either invalid or from an unsupported source. Please provide a valid {site} URL.[/red]\n"
                )
                sys.exit(0)

        elif args.platform in sources:
            intp = sources.index(args.platform) + 1
            handler(
                url=args.url,
                quality=args.quality,
                subtitle=args.subtitle,
                output=args.output,
            )
        else:
            console = Console()
            console.print(
                Align.center(
                    "[bold medium_purple]Keep ♾️ Videos 🌝[/bold medium_purple]"
                )
            )
            console.print(
                Align.center(
                    "[dim italic]Download and keep your ❤️  videos forever![/dim italic]"
                )
            )
            console.print()
            console.print("[bold]1. YouTube Downloader[/bold]")
            console.print("[bold]0. Exit[/bold]")
            console.print()
            console.print("[dim]More features coming soon...[/dim]")
            console.print()
            intp = int(Prompt.ask("[bold]Enter your choice[/bold]", choices=["1", "0"]))
            console.clear()
            handler()
    except KeyboardInterrupt or UnboundLocalError:
        console.print("\n[red]Exiting...[/red]\n")
        sys.exit(0)
    except ModuleNotFoundError as e:
        sys.exit(
            f"\n❌ Rich module not found! Please install the required dependencies.\n"
        )


if __name__ == "__main__":
    main()
