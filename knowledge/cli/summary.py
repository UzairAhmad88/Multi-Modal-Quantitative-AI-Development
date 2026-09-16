"""
CLI Tool: Research Knowledge Summary & Statistics.
"""

import json
from knowledge.summaries.summary_engine import ResearchSummaryEngine


def main():
    engine = ResearchSummaryEngine()
    summary = engine.generate_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
