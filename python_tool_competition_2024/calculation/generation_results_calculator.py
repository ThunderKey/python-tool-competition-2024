"""Calculator to gather generation results."""

from ..config import Config
from ..generation_results import TestGenerationResult, TestGenerationSuccess
from ..generator_plugins import find_generator
from ..target_finder import Target


def calculate_generation_result(target: Target, config: Config) -> TestGenerationResult:
    """Calculate the mutation analysis results."""
    generator = find_generator(config.generator_name)()
    result = generator.build_test(target.source)
    if isinstance(result, TestGenerationSuccess):
        target.test.parent.mkdir(parents=True, exist_ok=True)
        target.test.write_text(result.body, encoding="utf-8")
    return result
