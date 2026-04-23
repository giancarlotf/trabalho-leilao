import requests
from lxml import html

headers = {
            "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

class WSNoJS():

    @staticmethod
    def find_xpath(url, value):
        response = requests.get(url, headers=headers)
        tree = html.fromstring(response.content)
        value = value.strip()

        if '"' in value:
            value = f"'{value}'"

        matches = tree.xpath("//*[contains(normalize-space(text()), $val)]", val=value)

        if matches:
            return tree.getroottree().getpath(matches[0])

        return None

    @staticmethod
    def seek(url, xpath):
        response = requests.get(url, headers=headers)
        tree = html.fromstring(response.content)
        elements = tree.xpath(xpath)

        for el in elements:
            if hasattr(el, "text_content"):
                return el.text_content().strip()

        return None
