import sqlite3
from pathlib import Path
from datetime import datetime
from build.strip_front_matter import strip_front_matter

DB_PATH = "db/data.db"
POSTS_DIR = Path("post")
OUTPUT_DIR = Path("docs/tags")
OUTPUT_DIR.mkdir(exist_ok=True)

TEMPLATE_PATH = "./build/template.html"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # template を読み込み
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
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
            post_path = POSTS_DIR / filename
            if post_path.exists():
                text = post_path.read_text(encoding="utf-8")
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

# articles.append の部分を以下のように変更
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
        html_path = OUTPUT_DIR / f"{tag_name}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(output)

    conn.close()

if __name__ == "__main__":
    main()


#build.pyはdbの初期化，dbへの追加，index.htmlの作成
#test.pyはdocs/tags以下のhtmlの作成
#index.htmlを作る→dbを作る→dbを元にタグのhtmlを作る→タグのhtmlを参考にindex.htmlを更新する となっていて困る
#つまりbuild→test→buildの順番で実行する必要がある