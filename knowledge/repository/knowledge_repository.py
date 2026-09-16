"""
Knowledge Repository for Persisting and Searching Research Records.
"""

import os
import json
from typing import Dict, Any, List, Optional
from knowledge.schemas.knowledge_record import (
    ResearchKnowledgeRecord,
    ResearchClaim,
    ResearchJournalEntry,
    ReproducibilityCard,
    ExperimentFamily,
)


class KnowledgeRepository:
    """
    Storage & Indexing repository persisting records in artifacts/knowledge/.
    """

    def __init__(self, base_dir: str = "artifacts/knowledge"):
        self.base_dir = base_dir
        os.makedirs(os.path.join(self.base_dir, "records"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "claims"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "journal"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "reproducibility"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "families"), exist_ok=True)

    def save_record(self, record: ResearchKnowledgeRecord) -> str:
        filepath = os.path.join(self.base_dir, "records", f"{record.knowledge_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(record.model_dump_json(indent=2))
        return filepath

    def get_record(self, knowledge_id: str) -> Optional[ResearchKnowledgeRecord]:
        filepath = os.path.join(self.base_dir, "records", f"{knowledge_id}.json")
        if not os.path.exists(filepath):
            # Check by experiment_id
            for fn in os.listdir(os.path.join(self.base_dir, "records")):
                if fn.endswith(".json"):
                    fp = os.path.join(self.base_dir, "records", fn)
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("experiment_id") == knowledge_id or data.get("knowledge_id") == knowledge_id:
                            return ResearchKnowledgeRecord(**data)
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return ResearchKnowledgeRecord(**json.load(f))

    def list_records(self) -> List[ResearchKnowledgeRecord]:
        records = []
        rec_dir = os.path.join(self.base_dir, "records")
        for fn in os.listdir(rec_dir):
            if fn.endswith(".json"):
                fp = os.path.join(rec_dir, fn)
                with open(fp, "r", encoding="utf-8") as f:
                    records.append(ResearchKnowledgeRecord(**json.load(f)))
        return records

    def save_claim(self, claim: ResearchClaim) -> str:
        filepath = os.path.join(self.base_dir, "claims", f"{claim.claim_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(claim.model_dump_json(indent=2))
        return filepath

    def list_claims(self) -> List[ResearchClaim]:
        claims = []
        c_dir = os.path.join(self.base_dir, "claims")
        for fn in os.listdir(c_dir):
            if fn.endswith(".json"):
                with open(os.path.join(c_dir, fn), "r", encoding="utf-8") as f:
                    claims.append(ResearchClaim(**json.load(f)))
        return claims

    def save_journal_entry(self, entry: ResearchJournalEntry) -> str:
        filepath = os.path.join(self.base_dir, "journal", f"{entry.journal_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(entry.model_dump_json(indent=2))
        return filepath

    def list_journal_entries(self) -> List[ResearchJournalEntry]:
        entries = []
        j_dir = os.path.join(self.base_dir, "journal")
        for fn in os.listdir(j_dir):
            if fn.endswith(".json"):
                with open(os.path.join(j_dir, fn), "r", encoding="utf-8") as f:
                    entries.append(ResearchJournalEntry(**json.load(f)))
        return entries

    def save_reproducibility_card(self, card: ReproducibilityCard) -> str:
        filepath = os.path.join(self.base_dir, "reproducibility", f"{card.card_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(card.model_dump_json(indent=2))
        return filepath

    def get_reproducibility_card(self, card_id_or_exp_id: str) -> Optional[ReproducibilityCard]:
        rc_dir = os.path.join(self.base_dir, "reproducibility")
        for fn in os.listdir(rc_dir):
            if fn.endswith(".json"):
                fp = os.path.join(rc_dir, fn)
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("card_id") == card_id_or_exp_id or data.get("experiment_id") == card_id_or_exp_id:
                        return ReproducibilityCard(**data)
        return None
