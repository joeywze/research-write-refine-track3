"""Replace only the paragraphs selected for revision."""

from dataclasses import replace

from .contracts import Draft, fields, paragraph_text, text


def review_points(report, allowed):
    """Give each supplied rule or critic finding an explicit response target."""
    points = []
    for paragraph in report["paragraphs"]:
        pid = paragraph["paragraph_id"]
        if pid in allowed:
            for issue in paragraph["issues"]:
                points.append({"finding_id": "R:" + pid + ":" + issue["code"], "paragraph_id": pid,
                    "method": "rules", "category": issue["code"], "quote": "",
                    "explanation": issue["evidence"], "requested_action": issue["advice"]})
    for paragraph in report.get("qualitative_critic", {}).get("paragraphs", []):
        pid = paragraph["paragraph_id"]
        if pid in allowed:
            for finding in paragraph["findings"]:
                if finding["status"] == "ACTIONABLE":
                    points.append({"finding_id": "L:" + pid + ":" + finding["criterion"], "paragraph_id": pid,
                        "method": "llm", "category": finding["criterion"], "quote": finding["quote"],
                        "explanation": finding["explanation"], "requested_action": finding["safe_action"]})
    return points


def apply_guided_edits(draft, response, allowed, points):
    """Validate feedback coverage and edit evidence, without trusting a success claim."""
    fields(response, {"edits", "review_responses"}, "guided revision")
    candidate = apply_edits(draft, {"edits": response["edits"]}, allowed)
    if not isinstance(response["review_responses"], list):
        raise ValueError("review_responses must be a list")
    expected = {p["finding_id"]: p for p in points}
    if len(expected) != len(points):
        raise ValueError("Duplicate supplied review point")
    before = {p.paragraph_id: p.text for p in draft.paragraphs}
    after = {p.paragraph_id: p.text for p in candidate.paragraphs}
    seen, explained_changes = set(), set()
    for item in response["review_responses"]:
        fields(item, {"finding_id", "decision", "explanation", "before_quote", "after_quote"}, "review response")
        fid = item["finding_id"]
        if fid not in expected or fid in seen:
            raise ValueError("Unknown or duplicate review response")
        seen.add(fid)
        text(item["explanation"], "review response explanation")
        pid = expected[fid]["paragraph_id"]
        if item["decision"] == "EDITED":
            old_quote = text(item["before_quote"], "before quote")
            new_quote = text(item["after_quote"], "after quote")
            if before[pid] == after[pid] or old_quote == new_quote:
                raise ValueError("An EDITED response needs an actual text change and differing quotes")
            if old_quote not in before[pid] or new_quote not in after[pid]:
                raise ValueError("Edit evidence is absent from its paragraph")
            explained_changes.add(pid)
        elif item["decision"] == "NO_SAFE_EDIT":
            if item["before_quote"] != "" or item["after_quote"] != "":
                raise ValueError("NO_SAFE_EDIT must leave both quotes empty")
        else:
            raise ValueError("Unknown review response decision")
    if seen != set(expected):
        raise ValueError("Every supplied review point needs a response")
    changed = {pid for pid in before if before[pid] != after[pid]}
    if not changed <= explained_changes:
        raise ValueError("Every changed paragraph needs an EDITED review response")
    return candidate


def apply_edits(draft: Draft, response: dict, allowed: tuple[str, ...]) -> Draft:
    fields(response, {"edits"}, "revision")
    if not isinstance(response["edits"], list):
        raise ValueError("edits must be a list")
    known = {p.paragraph_id for p in draft.paragraphs}
    if not set(allowed) <= known:
        raise ValueError("Unknown target")
    edits = {}
    for edit in response["edits"]:
        fields(edit, {"paragraph_id", "text"}, "edit")
        pid = edit["paragraph_id"]
        if pid not in allowed or pid in edits:
            raise ValueError("Out-of-scope or duplicate paragraph edit")
        prose = paragraph_text(edit["text"])
        edits[pid] = prose
    return replace(draft, paragraphs=tuple(replace(p, text=edits.get(p.paragraph_id, p.text))
                                            for p in draft.paragraphs))
