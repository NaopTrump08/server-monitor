# -*- coding: utf-8 -*-
"""Fetch candidate photos from 360 image search (the only engine that returns
distinct results on this restricted network)."""
import os, io, sys, json, urllib.request, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "pool")
os.makedirs(OUT, exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

QUERIES = {
    "roujiamo": "\u8089\u5939\u998d",
    "paomo":    "\u7f8a\u8089\u6ce1\u998d",
    "yopo":     "\u6cb9\u6cfc\u9762",
    "liangpi":  "\u51c9\u76ae",
    "pit":      "\u79e6\u59cb\u7687\u5175\u9a6c\u4fd1 \u4e00\u53f7\u5751",
    "market":   "\u897f\u5b89 \u5c0f\u5403\u8857 \u591c\u5e02",
}


def search360(query, pages=2):
    urls, seen = [], set()
    for p in range(pages):
        u = "https://image.so.com/j?q=%s&src=srp&pn=%d" % (urllib.parse.quote(query), 30 * (p + 1))
        try:
            raw = urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": UA}), timeout=25
            ).read().decode("utf-8", "ignore")
            items = json.loads(raw).get("list", [])
        except Exception as e:
            print("      page %d failed: %s" % (p, e))
            continue
        for it in items:
            iu = it.get("img")
            if iu and iu not in seen:
                seen.add(iu)
                urls.append((iu, it.get("link") or iu, it.get("title") or ""))
    return urls


def main():
    only = sys.argv[1:] or list(QUERIES)
    manifest = {}
    mpath = os.path.join(OUT, "sources.json")
    if os.path.exists(mpath):
        manifest = json.load(open(mpath, encoding="utf-8"))
    for key in only:
        q = QUERIES[key]
        print("=== %s : %s ===" % (key, q))
        kept = 0
        for u, page, title in search360(q):
            if kept >= 8:
                break
            try:
                data = urllib.request.urlopen(
                    urllib.request.Request(u, headers={"User-Agent": UA,
                                                       "Referer": "https://image.so.com/"}),
                    timeout=20).read()
                im = Image.open(io.BytesIO(data)); im.load()
                if im.width < 800 or im.height < 600:
                    continue
                im = im.convert("RGB")
            except Exception:
                continue
            name = "%s_%02d.jpg" % (key, kept)
            im.save(os.path.join(OUT, name), quality=90, optimize=True)
            manifest[name] = {"query": q, "source": page, "title": title}
            kept += 1
            print("   %-14s %dx%d  %s" % (name, im.width, im.height, title[:38]))
        print("   kept", kept)
    json.dump(manifest, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
