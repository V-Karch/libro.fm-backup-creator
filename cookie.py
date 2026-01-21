import browser_cookie3
import requests


def find_libro_fm_cookies(
    verbose: bool = False,
) -> requests.cookies.RequestsCookieJar | None:
    jar = requests.cookies.RequestsCookieJar()

    for browser in browser_cookie3.all_browsers:
        try:
            cookies = browser(domain_name="libro.fm")
            for cookie in cookies:
                jar.set(
                    name=cookie.name,
                    value=cookie.value,
                    domain=cookie.domain,
                    path=cookie.path,
                )

            if jar:
                if verbose:
                    print(f"Found libro.fm cookies in {browser.__name__}")
                return jar

        except browser_cookie3.BrowserCookieError:
            if verbose:
                print(f"No cookies found in {browser.__name__}")
            continue

    return None
