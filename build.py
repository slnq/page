import glob
import os
from datetime import datetime
from build.strip_front_matter import strip_front_matter
from build.tagger_util import extract_tags
from db.add_post_tags import add_post_tags
from db.init_db import init_db

def build_index():
    with open("./build/template.html", encoding="utf-8") as f:
        template = f.read()

    articles = []
    for path in sorted(glob.glob("./post/*.md")):
        filename = os.path.basename(path)
        stem = filename.replace(".md", "")

        try:
            dt = datetime.strptime(stem, "%Y-%m-%d-%H-%M-%S")
            dt_str = dt.strftime("%Y/%m/%d %H:%M")
        except ValueError:
            continue

        with open(path, encoding="utf-8") as f:
            text = f.read()

        text = strip_front_matter(text)

        tags = extract_tags(text)
        
        init_db()
        add_post_tags(filename, tags)

        articles.append(f"""
        <article>
          <pre>{text}</pre>
          <pre class="tags">{" ".join("#"+t for t in tags)}</pre>
          <pre class="date">{dt_str}</pre>
        </article>
        """)

    content = "\n".join(articles)
    output = template.replace("{{content}}", content)

    os.makedirs("./docs", exist_ok=True)
    with open("./docs/index.html", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    build_index()
