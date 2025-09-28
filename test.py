import os
import sqlite3
from datetime import datetime
from build.strip_front_matter import strip_front_matter


def main():
    os.makedirs(os.path.join("docs", "tags"), exist_ok=True)

    conn = sqlite3.connect(os.path.join("db", "data.db"))
    cur = conn.cursor()

    # template を読み込み
    with open(os.path.join("build", "template.html"), encoding="utf-8") as f:
        template = f.read()

    # タグ一覧を取得
    cur.execute("SELECT id, name FROM tags")
    tags = cur.fetchall()

    for tag_id, tag_name in tags:
        # このタグに対応するポストのfilename一覧を取得
        cur.execute("""
            SELECT p.filename
            FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            WHERE pt.tag_id = ?
        """, (tag_id,))
        filenames = [row[0] for row in cur.fetchall()]

        if len(filenames) < 2:
            continue

        articles = []

        for filename in filenames:
            post_path = os.path.join("post", filename)
            if os.path.exists(post_path):
                with open(post_path, encoding="utf-8") as f:
                    text = f.read()
                text = strip_front_matter(text)

                # ファイル名から日時生成
                stem = filename.replace(".md", "")
                try:
                    dt = datetime.strptime(stem, "%Y-%m-%d-%H-%M-%S")
                    dt_str = dt.strftime("%Y/%m/%d %H:%M")
                except ValueError:
                    dt_str = ""

                # filename ごとのタグを取得
                cur.execute("""
                    SELECT t.name
                    FROM tags t
                    JOIN post_tags pt ON t.id = pt.tag_id
                    JOIN posts p ON p.id = pt.post_id
                    WHERE p.filename = ?
                """, (filename,))
                post_tags_list = [row[0] for row in cur.fetchall()]

                articles.append(f"""
<article>
  <pre>{text}</pre>
  <pre class="tags">{" ".join("#"+t for t in post_tags_list)}</pre>
  <pre class="date">{dt_str}</pre>
</article>
""")
            else:
                articles.append(f"<p>File not found: {filename}</p>")

        # template に埋め込み
        content = "\n".join(articles)
        output = template.replace("{{content}}", content)

        # HTML 書き出し
        html_path = os.path.join(os.path.join("docs", "tags"), f"{tag_name}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(output)

    conn.close()

if __name__ == "__main__":
    main()
