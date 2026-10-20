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
mac_tag = "pubky-macos-156.0.8073.4"
mac_asset = "pubky-chromium-156.0.8073.4-macos-arm64.zip"
windows_tag = "pubky-windows-156.0.8073.4"
windows_asset = "pubky-chromium-156.0.8073.4-windows-x64-mini-installer.exe"
assert f"{repo}/releases/download/{mac_tag}/{mac_asset}" in references.links
assert f"{repo}/releases/download/pubky-linux-${{version}}/pubky-chromium_${{version}}-1_amd64.deb" in page
assert f"{repo}/releases/download/{windows_tag}/{windows_asset}" in references.links
assert f"{repo}/commit/d48d707dcc2d8343f1c54ad1bff456d2621a1929" in references.links
assert f"{repo}/commit/e8c5d30f605f322b1f4688e1f2cb42d54ddc305b" not in references.links
assert f"{repo}/commit/d48d707dcc2d8343f1c54ad1bff456d2621a1929" in references.links
assert f"{repo}/commit/d48d707dcc2d8343f1c54ad1bff456d2621a1929" in references.links
assert re.search(r'<code id="mac-sha256">[a-f0-9]{64}</code>', page)
assert re.search(r'<code id="linux-sha256">[a-f0-9]{64}</code>', page)
assert re.search(r'<code id="windows-sha256">[a-f0-9]{64}</code>', page)
assert "Download not available yet" not in page and "@@" not in page
assert "Browser for the free internet" in page
assert "Censorship resistant" in page and "A familiar browser." not in page
assert "Try the experimental Mac build" not in page
assert "Before you install" not in page and "Install a separate test copy" not in page
assert page.count('class="download"') == 2
assert page.count("version=156.0.8073.4") == 1
assert f"{repo}/releases/download/pubky-linux-${{version}}/SHA256SUMS.txt" in page
assert "sha256sum -c SHA256SUMS.txt --ignore-missing" in page
assert 'sudo apt install "./pubky-chromium_${version}-1_amd64.deb"' in page
assert "Unknown publisher" in page and "terminal install avoids it" in page
assert "Not notarized yet" in page and "Privacy &amp; Security" in page
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
