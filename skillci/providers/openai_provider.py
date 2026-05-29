import json
import os

from skillci.evaluator.prompt import JUDGE_PROMPT
from skillci.providers.base import JudgeProvider
from skillci.schema.config import JudgeConfig, SkillTestCase
from skillci.schema.result import LLMTriggerResult
from skillci.schema.skill import Skill


class OpenAIJudgeProvider(JudgeProvider):
    def judge_trigger(
        self,
        skill: Skill,
        case: SkillTestCase,
        config: JudgeConfig,
    ) -> LLMTriggerResult:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Use --mode local or configure OPENAI_API_KEY."
            )

        prompt = JUDGE_PROMPT.format(
            skill_name=skill.name,
            skill_description=skill.description,
            skill_body_excerpt=skill.body[:1200],
            user_input=case.input,
        )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, timeout=config.timeout)
            response = client.responses.create(
                model=config.model,
                temperature=config.temperature,
                input=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            raw_text = response.output_text
            data = json.loads(raw_text)
            should_trigger = data.get("should_trigger")
            confidence = data.get("confidence")

            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                actual_trigger=bool(should_trigger) if should_trigger is not None else None,
                confidence=float(confidence) if confidence is not None else None,
                passed=False,
                reason=data.get("reason"),
                raw_response=raw_text,
            )
        except Exception as exc:
            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                passed=False,
                error=str(exc),
            )
