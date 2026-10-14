# -*- coding: utf-8 -*-
"""Search Bing Images with several queries per subject, dedupe by content hash,
keep only large-enough photos, and record where every file came from."""
import os, re, json, html, io, hashlib, urllib.request, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "photos")
os.makedirs(OUT, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

SUBJECTS = {
    "wall": ["\u897f\u5b89\u57ce\u5899 \u6c38\u5b81\u95e8",
             "\u897f\u5b89\u660e\u57ce\u5899 \u98ce\u666f",
             "Xian ancient city wall"],
    "muslim": ["\u897f\u5b89\u56de\u6c11\u8857 \u5c0f\u5403",
               "\u897f\u5b89\u56de\u6c11\u8857 \u7f8a\u8089\u4e32",
               "Xian Muslim Quarter street food"],
    "datang": ["\u897f\u5b89\u5927\u5510\u4e0d\u591c\u57ce",
               "\u5927\u5510\u4e0d\u591c\u57ce \u7ea2\u706f",
               "Datang Everbright City Xian night"],
    "night":  ["\u897f\u5b89\u949f\u697c \u591c\u666f",
               "Xian Bell Tower night"],
}


def bing(query, want=16):
    out, seen = [], set()
    for p in range(3):
        url = ("https://cn.bing.com/images/search?q=%s&first=%d&count=35"
               % (urllib.parse.quote(query), p * 35 + 1))
        try:
            raw = urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": UA}),
                timeout=25).read().decode("utf-8", "ignore")
        except Exception as e:
            print("      page %d failed: %s" % (p, e))
            continue
        for m in re.finditer(r'm="(\{[^"]*?\})"', raw):
            try:
                meta = json.loads(html.unescape(m.group(1)))
            except Exception:
                continue
            u = meta.get("murl")
            if u and u not in seen:
                seen.add(u)
                out.append((u, meta.get("purl", "")))
            if len(out) >= want:
                return out
    return out


def grab(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Referer": "https://cn.bing.com/"})
    data = urllib.request.urlopen(req, timeout=30).read()
    im = Image.open(io.BytesIO(data))
    im.load()
    if im.width < 900 or im.height < 600:
        raise ValueError("small %dx%d" % im.size)
    return im.convert("RGB"), data


def main():
    manifest, hashes = {}, {}
    for key, queries in SUBJECTS.items():
        print("=== %s ===" % key)
        kept = 0
        for q in queries:
            if kept >= 6:
                break
            print("   query:", q)
            for url, purl in bing(q):
                if kept >= 6:
                    break
                try:
                    im, data = grab(url)
                except Exception:
                    continue
                h = hashlib.md5(im.resize((32, 32)).tobytes()).hexdigest()
                if h in hashes:                       # seen under another query
                    continue
                hashes[h] = key
                name = "%s_%02d.jpg" % (key, kept)
                im.save(os.path.join(OUT, name), quality=90, optimize=True)
                manifest[name] = {"query": q, "source": purl or url}
                kept += 1
                print("      %-14s %dx%d  <- %s" % (name, im.width, im.height, (purl or url)[:58]))
        print("   kept %d" % kept)
    with open(os.path.join(OUT, "sources.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("\ntotal:", len(manifest))


if __name__ == "__main__":
    main()
