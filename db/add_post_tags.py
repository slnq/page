import sqlite3

DB_PATH = "db/data.db"

def add_post_tags(post_filename: str, tags: list[str]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO posts (filename) VALUES (?)", (post_filename,))
    c.execute("SELECT id FROM posts WHERE filename = ?", (post_filename,))
    post_id = c.fetchone()[0]

    for tag_name in tags:
        c.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        c.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = c.fetchone()[0]

        c.execute(
            "INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)",
            (post_id, tag_id)
        )

    conn.commit()
    conn.close()


# ------------------------------
# テストデータ追加
# ------------------------------
if __name__ == "__main__":
    # post1 -> tag1, tag2
    add_post_tags("post1.md", ["tag1", "tag2"])
    
    # post2 -> tag2, tag3
    add_post_tags("post2.md", ["tag2", "tag3"])

    # 確認
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    print("posts:", c.fetchall())

    c.execute("SELECT * FROM tags")
    print("tags:", c.fetchall())

    c.execute("SELECT * FROM post_tags")
    print("post_tags:", c.fetchall())
    conn.close()
