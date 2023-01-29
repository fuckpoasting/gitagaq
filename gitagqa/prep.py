from pathlib import Path
import re
import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import tiktoken


def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


@dataclass_json
@dataclass
class Chapter:
    index: int
    title: str
    alt_title: str
    prose: str
    book: str
    tokens: int


chapter_pattern = re.compile(r"CHAPTER [A-z]+\n")
metadata_pattern = re.compile(
    r"HERE [A-z]+ CHAPTER [A-z]+. OF THE BHAGAVAD-GITA[,]* Entitled \"(?P<title>[A-z].+)\,\" Or\s*\"(?P<alt_title>[A-z].+).\""
)


def get_parsed_text(raw_gita_path: Path):

    with open(raw_gita_path) as f:
        raw_text = f.read()
        matches = list(chapter_pattern.finditer(raw_text))

    parsed_text: list[Chapter] = list()

    for i in range(1, len(matches)):
        prev_span, current_span = matches[i - 1].span(), matches[i].span()
        current_chapter = matches[i - 1].group().strip()

        content = raw_text[prev_span[1] : current_span[0]].strip().split("\n")

        prose = None
        metadata = None

        for j in range(len(content)):
            if content[j].startswith("HERE ENDETH") or content[j].startswith(
                "HERE ENDS"
            ):
                metadata = " ".join(content[j:])
                prose = "\n".join(content[:j])
                break

        if prose is None or metadata is None:
            print(f"Something went wrong parsing data for chapter \n{content}")
            continue

        pattern = metadata_pattern.match(metadata)
        title = pattern.group("title")
        alt_title = pattern.group("alt_title")

        parsed_text.append(
            Chapter(
                index=i - 1,
                title=title,
                alt_title=alt_title,
                prose=prose,
                tokens=num_tokens_from_string(prose),
                book="gita",
            )
        )

    return parsed_text


if __name__ == "__main__":
    with open("./scratch/parsed_gita.json", "w") as f:
        json.dump(get_parsed_text("./datasets/raw_gita"), f)
