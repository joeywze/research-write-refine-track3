"""Replace only the paragraphs selected for revision."""

from dataclasses import replace

from .contracts import Draft, fields, paragraph_text


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
