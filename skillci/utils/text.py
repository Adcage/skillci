import re

STOP_WORDS = {
    "the",
    "a",
    "an",
    "to",
    "from",
    "and",
    "or",
    "of",
    "in",
    "on",
    "for",
    "with",
    "this",
    "that",
    "use",
    "when",
    "user",
    "asks",
    "skill",
    "helps",
    "help",
    "into",
    "根据",
    "这个",
    "把",
    "这些",
    "一下",
}


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*|[\u4e00-\u9fff]+", text.lower())
    return [token for token in tokens if token not in STOP_WORDS and len(token) > 1]


def token_set(text: str) -> set[str]:
    return set(tokenize(text))


def overlap_ratio(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0
    return len(left & right) / len(left)
