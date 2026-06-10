#!/usr/bin/env python3
"""Identificadores canônicos CARD / REQ / Fase — fonte única de regex."""
from __future__ import annotations

import re

CARD_ID_RE = re.compile(r"\bCARD-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b")
REQ_ID_RE = re.compile(r"\bREQ-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b")
PHASE_RE = re.compile(r"\b(?:FASE-\d+|SETUP|MVP)\b", re.I)

DELIVERY_HEADER_RE = re.compile(
    r"##\s+Entrega:\s*\[?(CARD-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\]?(?:\s*-\s*(.+))?",
    re.I,
)
BACKLOG_REQ_ROW_RE = re.compile(r"^\|\s*(REQ-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\s*\|", re.M | re.I)


def find_card_ids(text: str) -> list[str]:
    return sorted({m.group(0).upper() for m in CARD_ID_RE.finditer(text)})


def find_req_ids(text: str) -> list[str]:
    return sorted({m.group(0).upper() for m in REQ_ID_RE.finditer(text)})


def normalize_req_id(req_id: str) -> str:
    """REQ-001 permanece; REQ-Hub-PoC-Ready permanece slug."""
    req_id = req_id.strip().upper()
    m = re.fullmatch(r"REQ-(\d+)", req_id, re.I)
    if m:
        return f"REQ-{int(m.group(1)):03d}"
    return req_id


def parse_phase_from_block(block: str) -> str | None:
    m = re.search(r"^-\s*Fase:\s*((?:FASE-\d+|SETUP|MVP))", block, re.M | re.I)
    return m.group(1).upper() if m else None
