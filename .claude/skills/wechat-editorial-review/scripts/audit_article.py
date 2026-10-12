#!/usr/bin/env python3
"""Read-only structural audit for a Markdown WeChat article."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RISK_PATTERNS = {
    "absolute_or_universal": re.compile(r"唯一|永远|完全|必然|绝不|全部|任何一张|根本不"),
    "near_zero_or_free": re.compile(r"接近于零|趋近于零|免费资源|边际成本为零"),
    "typical_or_generalized": re.compile(r"通常|一般来说|大概率|所有人都|每一次都是"),
    "precise_delivery_claim": re.compile(
        r"(?:\d+|[一二两三四五六七八九十半]+)\s*"
        r"(?:天|周|个月|年|秒|分钟|个季度|季度).*"
        r"(?:变|跑通|追上|提前|完成)"
    ),
}

BANNED_TERMS = re.compile(r"赋能|抓手|闭环")
PLACEHOLDERS = re.compile(r"TODO|TBD|待补|待上传|需转图片|PLACEHOLDER", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s)>]+")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FIG_RE = re.compile(r"^:::fig\s+(\d+)/(\d+)\s*$")
FIG_CAPTION_RE = re.compile(r"!\[图\s*(\d+)[：:]", re.IGNORECASE)


def parse_front_matter(lines: list[str]) -> dict[str, str]:
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    section = ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        match = re.match(r"\s*([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        if indent == 0:
            section = key if not value else ""
            result[key] = value.strip().strip('"\'')
        elif section:
            result[f"{section}.{key}"] = value.strip().strip('"\'')
    return result


def table_column_count(line: str) -> int:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return 0
    escaped = False
    separators = 0
    for char in stripped:
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "|" and not escaped:
            separators += 1
        escaped = False
    return max(0, separators - 1)


def find_line_hits(lines: list[str], pattern: re.Pattern[str]) -> list[dict[str, Any]]:
    hits = []
    in_code = False
    for number, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        matches = sorted(set(pattern.findall(line)))
        if matches:
            hits.append({"line": number, "matches": matches, "text": line.strip()[:180]})
    return hits


def audit(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    front_matter = parse_front_matter(lines)

    images = []
    missing_assets = []
    for match in IMAGE_RE.finditer(text):
        raw = match.group(1).strip()
        if raw.startswith(("http://", "https://", "data:")):
            exists = None
        else:
            target = (path.parent / raw).resolve()
            exists = target.exists()
            if not exists:
                missing_assets.append(raw)
        images.append({"path": raw, "exists": exists})

    cover = front_matter.get("wechat.cover", "")
    cover_exists = None
    if cover and not cover.startswith(("http://", "https://", "data:")):
        cover_exists = (path.parent / cover).resolve().exists()
        if not cover_exists and cover not in missing_assets:
            missing_assets.append(cover)

    fig_cards = []
    for number, line in enumerate(lines, 1):
        match = FIG_RE.match(line)
        if match:
            fig_cards.append(
                {"line": number, "index": int(match.group(1)), "total": int(match.group(2))}
            )

    fig_sequence_ok = True
    if fig_cards:
        expected_total = len(fig_cards)
        fig_sequence_ok = (
            [item["index"] for item in fig_cards] == list(range(1, expected_total + 1))
            and all(item["total"] == expected_total for item in fig_cards)
        )

    image_caption_numbers = [int(value) for value in FIG_CAPTION_RE.findall(text)]
    max_table_columns = max((table_column_count(line) for line in lines), default=0)
    long_paragraphs = [
        {"line": number, "characters": len(line), "text": line[:180]}
        for number, line in enumerate(lines, 1)
        if len(line) > 180 and not line.lstrip().startswith(("|", "```", "http"))
    ]

    risk_hits = {name: find_line_hits(lines, pattern) for name, pattern in RISK_PATTERNS.items()}
    banned_hits = find_line_hits(lines, BANNED_TERMS)
    placeholder_hits = find_line_hits(lines, PLACEHOLDERS)

    return {
        "path": str(path.resolve()),
        "metadata": {
            "title": front_matter.get("title", ""),
            "digest": front_matter.get("wechat.digest", ""),
            "digest_characters": len(front_matter.get("wechat.digest", "")),
            "cover": cover,
            "cover_exists": cover_exists,
        },
        "counts": {
            "characters": len(text),
            "lines": len(lines),
            "parts": sum(1 for line in lines if line.startswith("# ")),
            "subheads": sum(1 for line in lines if line.startswith("## ")),
            "figure_cards": len(fig_cards),
            "insight_boxes": sum(1 for line in lines if line.startswith("> [!insight]")),
            "quote_boxes": sum(1 for line in lines if line.startswith("> [!quote]")),
            "urls": len(URL_RE.findall(text)),
            "images": len(images),
            "long_paragraphs": len(long_paragraphs),
        },
        "structure": {
            "figure_cards": fig_cards,
            "figure_sequence_ok": fig_sequence_ok,
            "image_caption_numbers": image_caption_numbers,
            "max_table_columns": max_table_columns,
        },
        "assets": {"images": images, "missing": sorted(set(missing_assets))},
        "risk_language": risk_hits,
        "banned_terms": banned_hits,
        "placeholders": placeholder_hits,
        "long_paragraphs": long_paragraphs,
    }


def print_text(report: dict[str, Any]) -> None:
    metadata = report["metadata"]
    counts = report["counts"]
    structure = report["structure"]
    print(f"Article: {report['path']}")
    print(f"Title: {metadata['title'] or '[missing]'}")
    print(f"Digest: {metadata['digest_characters']} characters")
    print(
        "Structure: "
        f"{counts['parts']} parts, {counts['subheads']} subheads, "
        f"{counts['figure_cards']} figure cards, {counts['images']} images"
    )
    print(
        "Evidence markers: "
        f"{counts['quote_boxes']} quote boxes, {counts['insight_boxes']} insight boxes, "
        f"{counts['urls']} URLs"
    )
    print(
        "Layout: "
        f"max {structure['max_table_columns']} table columns; "
        f"figure sequence {'OK' if structure['figure_sequence_ok'] else 'INVALID'}; "
        f"{counts['long_paragraphs']} source paragraphs over 180 characters"
    )
    missing = report["assets"]["missing"]
    print(f"Missing assets: {', '.join(missing) if missing else 'none'}")
    print(f"Placeholders: {len(report['placeholders'])}")
    print(f"Banned terms: {len(report['banned_terms'])}")
    for category, hits in report["risk_language"].items():
        print(f"Risk language [{category}]: {len(hits)} lines")
        for hit in hits[:8]:
            print(f"  L{hit['line']}: {hit['text']}")
        if len(hits) > 8:
            print(f"  ... {len(hits) - 8} more")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("article", type=Path, help="Markdown article to audit")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    if not args.article.is_file():
        parser.error(f"article not found: {args.article}")

    report = audit(args.article)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
