import os
import sqlite3
from build.strip_front_matter import strip_front_matter
from datetime import datetime


def build_index():
    # load HTML template
    with open("./build/template.html", encoding="utf-8") as f:
        template = f.read()

    # connect to SQLite database
    conn = sqlite3.connect("./db/data.db")
    cur = conn.cursor()

    # make tag list for each post
    cur.execute("""
        SELECT p.filename, t.name
        FROM posts p
        LEFT JOIN post_tags pt ON p.id = pt.post_id
        LEFT JOIN tags t ON pt.tag_id = t.id
        ORDER BY p.filename ASC
    """)
    rows = cur.fetchall()

    # map filename to list of tags
    post_tags_map = {}
    for filename, tag in rows:
        if filename not in post_tags_map:
            post_tags_map[filename] = []
        if tag:
            post_tags_map[filename].append(tag)

    # count posts per tag
    cur.execute("""
        SELECT t.name, COUNT(pt.post_id) as cnt
        FROM tags t
        JOIN post_tags pt ON t.id = pt.tag_id
        GROUP BY t.id
    """)
    tag_counts = {name: cnt for name, cnt in cur.fetchall()}

    # generate HTML articles
    articles = []
    for filename, tags in post_tags_map.items():
        stem = filename.replace(".md", "")
        try:
            dt = datetime.strptime(stem, "%Y-%m-%d-%H-%M-%S")
            dt_str = dt.strftime("%Y/%m/%d %H:%M")
        except ValueError:
            dt_str = ""

        path = os.path.join("./post", filename)
        if not os.path.exists(path):
            continue

        with open(path, encoding="utf-8") as f:
            text = f.read()
            text = strip_front_matter(text)

        tag_htmls = []
        for t in tags:
            if tag_counts.get(t, 0) >= 2:
                tag_htmls.append(f'<a href="./tags/{t}.html">#{t}</a>')
            else:
                tag_htmls.append(f'#{t}')

        articles.append(f"""
        <article>
          <pre>{text}</pre>
          <pre class="tags">{" ".join(tag_htmls)}</pre>
          <pre class="date">{dt_str}</pre>
        </article>
        """)

    # close database connection
    conn.close()

    # generate final HTML
    content = "\n".join(articles)
    output = template.replace("{{content}}", content)
    
    os.makedirs("./docs", exist_ok=True)
    with open("./docs/index.html", "w", encoding="utf-8") as f:
        f.write(output)
        

def build_tags():
    # create tags directory if not exists
    os.makedirs(os.path.join("docs", "tags"), exist_ok=True)

    # connect to SQLite database
    conn = sqlite3.connect(os.path.join("db", "data.db"))
    cur = conn.cursor()

    # load HTML template
    with open(os.path.join("build", "template.html"), encoding="utf-8") as f:
        template = f.read()

    # get all tags
    cur.execute("SELECT id, name FROM tags")
    tags = cur.fetchall()

    # find tags associated with 2 or more posts
    cur.execute("""
        SELECT t.name, COUNT(pt.post_id) as cnt
        FROM tags t
        JOIN post_tags pt ON t.id = pt.tag_id
        GROUP BY t.id
        HAVING cnt >= 2
    """)
    multi_post_tags = {row[0] for row in cur.fetchall()}

    for tag_id, tag_name in tags:
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

                stem = filename.replace(".md", "")
                try:
                    dt = datetime.strptime(stem, "%Y-%m-%d-%H-%M-%S")
                    dt_str = dt.strftime("%Y/%m/%d %H:%M")
                except ValueError:
                    dt_str = ""

                cur.execute("""
                    SELECT t.name
                    FROM tags t
                    JOIN post_tags pt ON t.id = pt.tag_id
                    JOIN posts p ON p.id = pt.post_id
                    WHERE p.filename = ?
                """, (filename,))
                post_tags_list = [row[0] for row in cur.fetchall()]

                tag_htmls = []
                for t in post_tags_list:
                    if t in multi_post_tags:
                        tag_htmls.append(f'<a href="./{t}.html">#{t}</a>')
                    else:
                        tag_htmls.append(f'#{t}')

                articles.append(f"""
<article>
  <pre>{text}</pre>
  <pre class="tags">{" ".join(tag_htmls)}</pre>
  <pre class="date">{dt_str}</pre>
</article>
""")
            else:
                articles.append(f"<p>File not found: {filename}</p>")

        # generate HTML for this tag
        content = "\n".join(articles)
        output = template.replace("{{content}}", content)

        # write to file
        html_path = os.path.join(os.path.join("docs", "tags"), f"{tag_name}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(output)

    # close database connection
    conn.close()


if __name__ == "__main__":
    build_index()
    build_tags()
