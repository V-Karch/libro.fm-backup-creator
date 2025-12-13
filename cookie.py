import browser_cookie3

def find_libro_fm_cookies() -> dict | None:
    found_cookies = {}
    for browser in browser_cookie3.all_browsers:
        try: # This can fail if the browser isn't present
            for cookie in browser(domain_name="libro.fm"):
                found_cookies[cookie.name] = cookie.value
            
            print(f"Found https://libro.fm/ cookies in browser {browser.__name__}")
            return found_cookies
        except browser_cookie3.BrowserCookieError:
            print(f"Failed to find https://libro.fm/ cookies with browser {browser.__name__}")
            continue
        
    return None
