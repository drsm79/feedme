from utils import load_feeds, get_feed_content
from pathlib import Path

root = Path("fedhugo/content/articles/")


def store_feeds(size=0):
    feeds = load_feeds()
    content = get_feed_content(feeds, do_sampling=False, size=size)
    i = 0
    print(f"have {len(content)} articles")
    for c in content:
        file = Path(c.slug).with_suffix(".md")
        file = root / file
        if not file.exists():
            file.open("w")
            content = "\n".join(
                ["---", c.to_yaml(), "---", c.summary, f"[Read More]({c.url})"]
            )
            file.write_text(content)
            i += 1
            if i == size:
                break
    print(f"Wrote {i} files (expected no more than {size})")


def clean(age=14):
    """
    Delete files more than age days old
    """
    pass
