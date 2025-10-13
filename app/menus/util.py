import app.menus.banner as banner
from app.util import get_user_info, load_api_key
ascii_art = banner.load("https://me.mashu.lol/mebanner880.png", globals())

from html.parser import HTMLParser
import os
import re
import textwrap

def clear_screen():
    print("Clearing screen...")
    user_info = get_user_info(load_api_key())
    os.system('cls' if os.name == 'nt' else 'clear')
    if ascii_art:
        ascii_art.to_terminal(columns=55)

    if user_info:
        credit = user_info.get("credit", 0)
        premium_credit = user_info.get("premium_credit", 0)
        
        width = 55 
        print("=" * width)
        print(f" Credit: {credit} | Premium Credit: {premium_credit} ".center(width))
        print("=" * width)
        print("")
        

def pause():
    input("\nPress enter to continue...")

class HTMLToText(HTMLParser):
    def __init__(self, width=80):
        super().__init__()
        self.width = width
        self.result = []
        self.in_li = False

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.in_li = True
        elif tag == "br":
            self.result.append("\n")

    def handle_endtag(self, tag):
        if tag == "li":
            self.in_li = False
            self.result.append("\n")

    def handle_data(self, data):
        text = data.strip()
        if text:
            if self.in_li:
                self.result.append(f"- {text}")
            else:
                self.result.append(text)

    def get_text(self):
        # Join and clean multiple newlines
        text = "".join(self.result)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        # Wrap lines nicely
        return "\n".join(textwrap.wrap(text, width=self.width, replace_whitespace=False))

def display_html(html_text, width=80):
    parser = HTMLToText(width=width)
    parser.feed(html_text)
    return parser.get_text()