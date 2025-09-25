import fugashi
import re

def extract_tags(text: str, stopwords_path: str = "./build/stopwords.txt"):

    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    with open(stopwords_path, encoding="utf-8") as f:
        stopwords = set(f.read().strip().split(","))

    tagger = fugashi.Tagger()
    words = list(tagger(text))

    nouns = []
    buffer = ""
    keijoshi_buffer = ""

    for word in words:
        f = word.feature

        is_sahen = f.pos1 == "名詞" and f.pos3 == "サ変可能"
        is_valid_noun = f.pos1 == "名詞" and f.pos3 not in ["副詞可能", "形状詞"]
        is_valid_suffix = (
            f.pos1 == "接尾辞" and f.pos2 == "名詞的" and f.pos3 != "副詞可能"
        )
        is_keijoshi = f.pos1 == "形状詞"

        if is_valid_noun or is_sahen:
            if keijoshi_buffer:
                buffer += keijoshi_buffer
                keijoshi_buffer = ""
            buffer += word.surface
        elif is_valid_suffix:
            if keijoshi_buffer:
                buffer += keijoshi_buffer
                keijoshi_buffer = ""
            buffer += word.surface
        elif is_keijoshi:
            keijoshi_buffer += word.surface
        else:
            if buffer:
                if buffer not in stopwords:
                    nouns.append(buffer)
                buffer = ""
            keijoshi_buffer = ""

    if buffer:
        if buffer not in stopwords:
            nouns.append(buffer)

    return nouns
