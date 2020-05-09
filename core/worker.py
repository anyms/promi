from selenium import webdriver
import json
from time import sleep
from selenium.webdriver.chrome.options import Options

from utils.argparse import ArgParse


class Promoter:
    def __init__(self):
        self.groups = []
        self.accounts = []

        self.argparse = ArgParse(25, usage="python promoter.py [options]")
        self.argparse.add_argument(["-h", "-help"], description="show help", is_flag=True)
        self.argparse.add_argument(["-accounts"], example="[group, account]", description="Add a new facebook account")
        self.argparse.add_argument(["-run"], description="Start posting your content to all groups", is_flag=True)
        self.args = self.argparse.parse()

        if self.args.run:
            with open("post.txt", "rt") as f:
                self.post = f.read().replace("\n", "\\n")
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("start-maximized")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--log-level=3")
            self.browser = webdriver.Chrome("bin/chromedriver.exe", options=options)

    def run(self):
        if self.args.h:
            self.argparse.print_help()
        elif self.args.run:
            with open(self.args.accounts, "rt") as f:
                for line in f:
                    if line.strip() != "":
                        nodes = line.split(":")
                        self.accounts.append({
                            "email": nodes[0].strip(),
                            "password": nodes[1].strip()
                        })
            for acc in self.accounts:
                self.promote(acc["email"], acc["password"])

            self.browser.quit()

    def promote(self, email, password):
        print("* Logging in...")
        self.browser.get("https://facebook.com")
        self.fill_input("input[type='email']", email)
        self.fill_input("input[type='password']", password)
        self.click("input[value='Log In']")
        print("* Logged in as {}".format(email))

        sleep(5)

        self.update_groups()

        for group in self.groups:
            print("* Going to group {}".format(group))
            self.browser.get(group)
            print("* Preparing your post...")
            try:
                self.browser.execute_script("""
                var box = document.querySelector('div[aria-label="Create a post"]');
                var inp = box.querySelector('textarea');
                inp.value = "{}";
                inp.click();
                """.format(self.post))

                sleep(10)

                try:
                    self.click("div[aria-label='Create a post'] button[type='submit']", 1)
                    print("* Successfully posted!")
                except:
                    self.click("div[aria-label='Create a post'] button[type='submit']", 0)
                    print("* Successfully posted!")

                sleep(5)
            except:
                print("! Err: you can not post to this group: {}".format(group))

        self.logout()
        sleep(2)

    def update_groups(self):
        print("* Fetching groups...")
        self.browser.get("https://www.facebook.com/groups")
        while True:
            is_loadmore = self.browser.execute_script("""
            var sidebar = document.querySelector('div[stickto="WINDOW"]');
            var loadMore = sidebar.querySelectorAll("span");
            if (loadMore[loadMore.length - 1].textContent === "See More") {
                return true;
            }
            return false;
            """)

            if not is_loadmore:
                break

            self.browser.execute_script("""
            var sidebar = document.querySelector('div[stickto="WINDOW"]');
            var loadMore = sidebar.querySelectorAll("span");
            loadMore[loadMore.length - 1].click();
            """)
            sleep(5)

        self.groups = self.browser.execute_script("""
        var els = document.querySelectorAll("a[href^='/groups/'][title][class]");
        var groups = [];
        for (var i = 0; i < els.length; i++) {
            groups.push("https://www.facebook.com" + els[i].getAttribute("href"));
        }
        return groups;
        """)

    def logout(self):
        print("* Logging out...")
        self.browser.execute_script("""
        document.querySelector("#userNavigationLabel").click();
        """)
        sleep(4)
        self.browser.execute_script("""
        document.querySelector('a[data-gt*="menu_logout"]').click();
        """)

    def click(self, selector, position=0):
        self.browser.execute_script("""
        document.querySelectorAll("{}")[{}].click();
        """.format(selector, position))

    def fill_input(self, selector, value, position=0):
        self.browser.execute_script("""
        document.querySelectorAll("{}")[{}].value = "{}";
        """.format(selector, position, value))

    def wait_for(self, selector):
        while True:
            el_count = self.browser.execute_script("""
            return document.querySelectorAll("{}").length;
            """)
            if el_count != 0:
                break
            sleep(500)


if __name__ == "__main__":
    promoter = Promoter()
    promoter.run()
