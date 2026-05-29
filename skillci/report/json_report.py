from skillci.schema.report import SkillCIReport


def render_json(report: SkillCIReport) -> str:
    return report.model_dump_json(indent=2)
