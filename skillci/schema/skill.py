from pathlib import Path

from pydantic import BaseModel, Field


class Skill(BaseModel):
    path: Path
    skill_md_path: Path
    name: str
    description: str
    frontmatter: dict[str, object] = Field(default_factory=dict)
    body: str = ""
    headings: list[str] = Field(default_factory=list)
    references: list[Path] = Field(default_factory=list)
    scripts: list[Path] = Field(default_factory=list)
    assets: list[Path] = Field(default_factory=list)
