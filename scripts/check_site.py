"""Check the static download page and its release metadata contract."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re

ROOT = Path(__file__).resolve().parents[1] / "docs"


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            assert values["id"] not in self.ids, "Duplicate element ID"
            self.ids.add(values["id"])
        if tag == "a":
            self.links.append(values.get("href", ""))
        if tag in ("img", "script", "link"):
            ref = values.get("src") or values.get("href")
            if ref:
                self.images.append(ref)


page = (ROOT / "index.html").read_text()
references = References()
references.feed(page)
repo = "https://github.com/pubky/pubky-chromium"
mac_tag = "pubky-macos-156.0.8073.5"
mac_asset = "pubky-chromium-156.0.8073.5-macos-arm64.zip"
windows_tag = "pubky-windows-156.0.8073.5"
windows_asset = "pubky-chromium-156.0.8073.5-windows-x64-mini-installer.exe"
linux_tag = "pubky-linux-156.0.8078.48"
linux_asset = "pubky-chromium_156.0.8078.48-1_amd64.deb"
assert f"{repo}/releases/download/{mac_tag}/{mac_asset}" in references.links
install = re.search(r'<code id="linux-install">(.*?)</code>', page, re.S)
assert install, "Linux install commands missing"
assert install.group(1) == (f'wget "{repo}/releases/download/{linux_tag}/{linux_asset}"\n'
                            f'sudo apt install "./{linux_asset}"'), install.group(1)
assert f"{repo}/releases/download/{windows_tag}/{windows_asset}" in references.links
assert f"{repo}/commit/ccb3ece482ab5d90715a77ebf5e268b8b5e54503" in references.links
assert f"{repo}/commit/e8c5d30f605f322b1f4688e1f2cb42d54ddc305b" not in references.links
assert f"{repo}/commit/ccb3ece482ab5d90715a77ebf5e268b8b5e54503" in references.links
assert f"{repo}/commit/4143f9e4329fe0eed04aa807c0ee9cf6cf82e105" in references.links
assert re.search(r'<code id="mac-sha256">[a-f0-9]{64}</code>', page)
assert re.search(r'<code id="linux-sha256">[a-f0-9]{64}</code>', page)
assert "09d8e584e9277ea7b607ee119df0be21abe83c8fe0ada0e081574eb6953cb1de" in page
assert re.search(r'<code id="windows-sha256">[a-f0-9]{64}</code>', page)
assert "7b5ecf705d020e949172f3728c28677d55517be64412ea7695ac675a731d7a72" in page
assert "Download not available yet" not in page and "@@" not in page
assert "Browser for the free internet" in page
assert "Censorship resistant" in page and "A familiar browser." not in page
assert "Try the experimental Mac build" not in page
assert "Before you install" not in page and "Install a separate test copy" not in page
assert page.count('class="download"') == 2
assert "version=" not in page and "SHA256SUMS" not in page and "sha256sum" not in page
assert "Unknown publisher" in page and "terminal install avoids it" in page
assert "Not notarized yet" not in page and "Privacy &amp; Security" not in page
assert "5da6a1fef5adc03d4af0ce8a3ab91751e6d2a18e455d69a07d0e3785a59b55e8" in page
assert "pubky-newtab-dark.png" not in page and not (ROOT / "assets" / "pubky-newtab-dark.png").exists()
assert "github.com/MCarlomagno" not in page
assert references.images and all(not urlsplit(ref).scheme for ref in references.images)
for ref in references.links + references.images:
    url = urlsplit(ref)
    if url.scheme:
        assert url.scheme == "https", ref
        continue
    assert ref and not ref.startswith("/") and ".." not in Path(url.path).parts, ref
    assert (ROOT / (url.path or "index.html")).is_file(), ref
    if url.fragment:
        assert url.fragment in references.ids, ref
assert not any(p.suffix.lower() in {".zip", ".dmg", ".pkg", ".dylib", ".deb", ".exe"} for p in ROOT.rglob("*"))
print("Site references, local assets and Mac/Linux/Windows release metadata OK")
