import hashlib
import re
import urllib.parse

import requests
import requests_cache
from bs4 import BeautifulSoup

PREFIX = "../boons-gh-page/"

requests_cache.install_cache("boons_cache")

page_list = [
    "https://hades.fandom.com/wiki/Aphrodite",
    "https://hades.fandom.com/wiki/Ares",
    "https://hades.fandom.com/wiki/Artemis",
    "https://hades.fandom.com/wiki/Athena",
    "https://hades.fandom.com/wiki/Demeter",
    "https://hades.fandom.com/wiki/Dionysus",
    "https://hades.fandom.com/wiki/Hermes",
    "https://hades.fandom.com/wiki/Poseidon",
    "https://hades.fandom.com/wiki/Zeus",
]

all_names = {}


# noinspection PyShadowingNames
def extract_table(url):
    page = requests.get(url)
    bs = BeautifulSoup(page.text, "html.parser")
    (table,) = bs.find_all("table", class_="wikitable sortable boonTableSB")

    cells = table.find_all("td", class_="boonTableName")
    for cell in cells:
        # extract and save image
        image = cell.find("a")
        href = image.attrs["href"]
        img = requests.get(href)
        (file_name,) = filter(lambda s: s.endswith(".png"), href.split("/"))
        file_name = "".join(
            x for x in urllib.parse.unquote(file_name) if x.isalnum() or x == "."
        )
        with open(f"{PREFIX}images/{file_name}", "wb") as fp:
            fp.write(img.content)

        # extract name
        name_tag = cell.find("b")
        boon_name = name_tag.string
        boon_md5 = hashlib.md5(boon_name.encode()).hexdigest()
        all_names[boon_name] = boon_md5

        # replace name tag with link
        b_tag = bs.new_tag("b")
        b_tag.string = boon_name
        img_tag = bs.new_tag("img")
        img_tag.attrs["src"] = f"images/{file_name}"
        img_tag.attrs["width"] = "120"
        img_tag.attrs["id"] = boon_md5
        image.replace_with(img_tag)
        name_tag.replace_with(b_tag)

    return table


BASE_PAGE = """<!DOCTYPE html>
<html>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
<body>
<div class="container">
    <nav class="navbar navbar-expand-lg sticky-top navbar-light bg-light">
        <div class="container-fluid">
            <ul class="nav">
                <li class="nav-item"><a class="nav-link" href="#Aphrodite">Aphrodite</a></li>
                <li class="nav-item"><a class="nav-link" href="#Ares">Ares</a></li>
                <li class="nav-item"><a class="nav-link" href="#Artemis">Artemis</a></li>
                <li class="nav-item"><a class="nav-link" href="#Athena">Athena</a></li>
                <li class="nav-item"><a class="nav-link" href="#Demeter">Demeter</a></li>
                <li class="nav-item"><a class="nav-link" href="#Dionysus">Dionysus</a></li>
                <li class="nav-item"><a class="nav-link" href="#Hermes">Hermes</a></li>
                <li class="nav-item"><a class="nav-link" href="#Poseidon">Poseidon</a></li>
                <li class="nav-item"><a class="nav-link" href="#Zeus">Zeus</a></li>
            </ul>
        </div>
    </nav>
    <div class="mystuff"></div
</div>
</body>
</html>"""

bs = BeautifulSoup(BASE_PAGE, "html.parser")
body = bs.find("div", class_="mystuff")

for url in page_list:
    table = extract_table(url)
    header = bs.new_tag("h1")

    god_name = url.split("/")[-1]
    header.string = god_name
    header.attrs["id"] = god_name
    body.append(header)
    body.append(table)

# add links
for boon_name, boon_link in all_names.items():
    for txt in bs.find_all(text=re.compile(boon_name)):
        before, after = txt.split(boon_name)
        link_tag = bs.new_tag("a")
        link_tag.attrs["href"] = f"#{boon_link}"
        link_tag.string = boon_name

        txt.replace_with(before, link_tag, after)


for table in bs.find_all("table"):
    table.attrs["class"] = "table"

with open(f"{PREFIX}index.html", "w") as fp:
    fp.write(str(bs))
