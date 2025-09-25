import glob
import os
from datetime import datetime
from tagger_util import extract_tags  # ← ここでインポート

def strip_front_matter(text: str) -> str:
    lines = text.splitlines()
    if len(lines) > 0 and lines[0].strip() == "---":
        try:
            end_idx = lines[1:].index("---") + 1
            return "\n".join(lines[end_idx+1:])
        except ValueError:
            return text
    return text

def build_index():
    with open("template.html", encoding="utf-8") as f:
        template = f.read()

    articles = []
    for path in sorted(glob.glob("./*.md")):
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

        # ここでタグ抽出
        tags = extract_tags(text)

        articles.append(f"""
        <article>
          <pre>{text}</pre>
          <pre class="tags">{" ".join("#"+t for t in tags)}</pre>
          <pre class="date">{dt_str}</pre>
        </article>
        """)

    content = "\n".join(articles)
    output = template.replace("{{content}}", content)

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    build_index()
