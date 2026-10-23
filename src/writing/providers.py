"""Call the Responses API and record usage against a token allowance."""

from dataclasses import dataclass
import json
from time import perf_counter

from .contracts import digest
from .prompts import PROMPT_VERSION


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class TokenBudget:
    limit: int = 200_000
    charged: int = 0

    def __post_init__(self):
        if type(self.limit) is not int or self.limit < 1:
            raise ValueError("Token limit must be a positive integer")

    def reserve(self, amount: int):
        if self.charged + amount > self.limit:
            raise BudgetExceeded("The next call's estimated token usage would exceed the run limit")
        self.charged += amount


class OpenAIJSON:
    """Use a chosen model without automatic retries.

    Reserve UTF-8 input bytes plus the output limit and 1024 overhead tokens.
    Replace the estimate with reported usage when available. If usage is unknown,
    including after a failed request, retain the estimate. This is a local budget
    check rather than an exact token count or billing guarantee.
    """

    test_only = False

    def __init__(self, model: str, budget: TokenBudget, store, client=None, timeout: float = 90,
                 stage: str = "unspecified"):
        if not isinstance(model, str) or not model.strip():
            raise ValueError("An explicit model ID is required")
        if client is None:
            from openai import OpenAI
            client = OpenAI(max_retries=0, timeout=timeout)
        self.model = model
        self.budget = budget
        self.store = store
        self.client = client
        self.stage = stage

    def generate(self, task: str, instructions: str, payload: dict, schema: dict,
                 max_output_tokens: int) -> dict:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)
        reservation = len((instructions + encoded).encode("utf-8")) + max_output_tokens + 1024
        self.budget.reserve(reservation)
        start = perf_counter()
        usage = None
        response = None
        error_type = None
        data = None
        try:
            response = self.client.responses.create(
                model=self.model, instructions=instructions, input=encoded,
                max_output_tokens=max_output_tokens, store=False,
                text={"format": {"type": "json_schema", "name": "stage_b_response",
                                 "schema": schema, "strict": True}},
            )
            raw_usage = getattr(response, "usage", None)
            if raw_usage is not None:
                incoming = getattr(raw_usage, "input_tokens", None)
                outgoing = getattr(raw_usage, "output_tokens", None)
                if type(incoming) is int and type(outgoing) is int and min(incoming, outgoing) >= 0:
                    usage = {"input_tokens": incoming, "output_tokens": outgoing}
                    self.budget.charged += incoming + outgoing - reservation
            if getattr(response, "status", None) != "completed":
                raise ValueError("The model response did not complete")
            raw = getattr(response, "output_text", "")
            if not raw:
                raise ValueError("Model returned no usable JSON (possibly a refusal)")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
            return data
        except Exception as error:
            error_type = type(error).__name__
            raise
        finally:
            self.store.event("model_call", task=task, model=self.model,
                             stage=self.stage, resolved_model=getattr(response, "model", None),
                             prompt_version=PROMPT_VERSION, prompt_hash=digest(instructions),
                             payload_hash=digest(payload), schema_hash=digest(schema),
                             max_output_tokens=max_output_tokens, reservation_tokens=reservation,
                             usage=usage, usage_basis="reported" if usage is not None else "reserved_unknown",
                             charged_tokens=self.budget.charged, elapsed_seconds=perf_counter() - start,
                             response_id=getattr(response, "id", None), error_type=error_type,
                             response=data)
