from skillci.schema.config import SkillTestCase, ThresholdConfig
from skillci.schema.result import LocalTriggerResult
from skillci.schema.skill import Skill
from skillci.utils.text import overlap_ratio, token_set

DOMAIN_TERMS = {
    "api",
    "openapi",
    "swagger",
    "rest",
    "controller",
    "controllers",
    "route",
    "routes",
    "fastapi",
    "spring",
    "documentation",
    "docs",
    "schema",
    "request",
    "response",
    "接口",
    "文档",
}


def evaluate_local_trigger(
    skill: Skill,
    case: SkillTestCase,
    thresholds: ThresholdConfig,
) -> LocalTriggerResult:
    case_terms = token_set(" ".join([case.input, *case.tags]))
    description_terms = token_set(skill.description)
    body_terms = token_set(skill.body)
    heading_terms = token_set(" ".join(skill.headings))
    tag_terms = set(case.tags)

    description_similarity = overlap_ratio(case_terms, description_terms)
    keyword_overlap = overlap_ratio(case_terms, body_terms)
    domain_matches = case_terms & DOMAIN_TERMS
    domain_term_match = min(len(domain_matches) / 3, 1)
    heading_match = overlap_ratio(case_terms, heading_terms)
    tag_match = min(
        len(tag_terms & (description_terms | body_terms | DOMAIN_TERMS)) / max(len(tag_terms), 1),
        1,
    )

    trigger_score = round(
        0.45 * description_similarity
        + 0.20 * keyword_overlap
        + 0.15 * domain_term_match
        + 0.10 * heading_match
        + 0.10 * tag_match,
        4,
    )
    actual_trigger = trigger_score >= thresholds.trigger_score
    passed = actual_trigger == case.expected_trigger
    searchable_terms = description_terms | body_terms | heading_terms | DOMAIN_TERMS
    matched_terms = sorted(case_terms & searchable_terms)
    missing_terms = sorted(case_terms - set(matched_terms))
    reason = f"score={trigger_score}; matched_terms={', '.join(matched_terms) or 'none'}"

    return LocalTriggerResult(
        case_name=case.name,
        expected_trigger=case.expected_trigger,
        actual_trigger=actual_trigger,
        trigger_score=trigger_score,
        passed=passed,
        reason=reason,
        matched_terms=matched_terms,
        missing_terms=missing_terms,
    )
