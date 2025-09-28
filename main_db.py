import sys
import os
from build.strip_front_matter import strip_front_matter # delete information in markdown file
from build.tagger_util import extract_tags	 			# extract tags from text using morphological analysis
from db.add_post_tags import add_post_tags				# add post and tags to database


def process_new_post(md_path: str):
    
	# error if markdown file does not exist
    if not os.path.exists(md_path):
        print(f"File {md_path} does not exist.")
        return

	# get contents of markdown file
    filename = os.path.basename(md_path)
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    text = strip_front_matter(text)
    
	# get tags from text
    tags = extract_tags(text)

	# add post and tags to db
    add_post_tags(filename, tags)
    
	# print result
    print(f"Processed {filename}: tags = {tags}")


if __name__ == "__main__":
    
	# check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main_db.py <new_post.md>")
        sys.exit(1)

	# morphological analysis and add to db
    md_file = sys.argv[1]
    process_new_post(md_file)
