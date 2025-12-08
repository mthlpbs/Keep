import urllib3


class LinkError(Exception):
    """
    Exception raised for invalid or unsupported YouTube URLs.
    """

    def __init__(
        self,
        msg: str = "The provided URL is either invalid or from an unsupported source. Please provide a valid youtube URL.",
    ):
        super().__init__(msg)


class FileError(Exception):
    """
    Exception raised for unsupported file types or non-existent files.
    """

    def __init__(self, path: str):
        super().__init__(f"{path} is not supported file or doesn't exist.")


class test:
    @staticmethod
    def check_internet_conn():
        """
        Checks if there is an active internet connection.

        Returns:
            bool: True if there is an internet connection, False otherwise.
        """
        try:
            http = urllib3.PoolManager(timeout=3.0)
            r = http.request("GET", "https://google.com", preload_content=False)
            code = r.status
            r.release_conn()
            if code == 200:
                return True
            else:
                return False
        except urllib3.exceptions.HTTPError:
            return False


class recognizer:
    @staticmethod
    def url(link: str) -> str:
        """
        Recognizes the video site name from the provided URL.

        Args:
            link (str): The URL to be checked.

        Returns:
            str: The name of the video site if recognized, otherwise 'none'.
        """
        import re

        regex = {
            "youtube": r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})(?:&[^#\s]*)?$",
        }
        for site, pattern in regex.items():
            if re.match(pattern, link):
                return site
        return "none"


def main(): ...


if __name__ == "__main__":
    main()
