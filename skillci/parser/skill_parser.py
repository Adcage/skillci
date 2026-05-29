import re
from pathlib import Path

import yaml

from skillci.schema.skill import Skill


class SkillParseError(ValueError):
    pass


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
REFERENCE_RE = re.compile(r"`((?:references|scripts|assets)/[^`]+)`")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def parse_skill(skill_path: Path) -> Skill:
    skill_path = skill_path.resolve()
    skill_md_path = skill_path / "SKILL.md"
    if not skill_md_path.exists():
        raise SkillParseError(f"SKILL.md not found: {skill_md_path}")

    raw = skill_md_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise SkillParseError(f"Invalid or missing frontmatter: {skill_md_path}")

    frontmatter_text, body = match.groups()
    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as exc:
        raise SkillParseError(f"Invalid YAML frontmatter: {skill_md_path}") from exc

    name = str(frontmatter.get("name", "")).strip()
    description = str(frontmatter.get("description", "")).strip()
    if not name:
        raise SkillParseError("Missing required frontmatter field: name")
    if not description:
        raise SkillParseError("Missing required frontmatter field: description")

    headings = [heading.strip() for _, heading in HEADING_RE.findall(body)]
    referenced_paths = [Path(value) for value in REFERENCE_RE.findall(body)]
    scripts = [path for path in referenced_paths if path.parts and path.parts[0] == "scripts"]
    assets = [path for path in referenced_paths if path.parts and path.parts[0] == "assets"]
    references = [path for path in referenced_paths if path.parts and path.parts[0] == "references"]

    return Skill(
        path=skill_path,
        skill_md_path=skill_md_path,
        name=name,
        description=description,
        frontmatter=frontmatter,
        body=body,
        headings=headings,
        references=references,
        scripts=scripts,
        assets=assets,
    )
