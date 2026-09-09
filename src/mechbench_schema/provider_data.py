"""Models someone else runs (task 000351, epic 000334).

Four shapes cross a repo boundary once a protocol can call an external
provider, and they belong here rather than in any one consumer:

- `EndpointRef` — the third form of a model reference. A base plus an
  adapter stack says WHERE weights come from; an endpoint says WHO RUNS
  THEM, and that is a different kind of fact: there are no weights of
  ours to fuse, and the node that names one must carry a spending cap.
- `CallProvenance` — what one call to someone else's model cost and who
  answered it. Provenance is the reason to own the transport at all: a
  result that cannot say which dated model version produced it is a
  claim rather than a measurement.
- `Agent` — a participant: a model reference, a system prompt, tools,
  sampling. A conversation is a graph of these, so an agent has to be
  an object the bench can store and a protocol can reference.
- `Transcript` — what happened between them. Each message records the
  participant that produced it AND the role it was SEEN as, because in
  a two-model conversation each side perceives the other as the user:
  one exchange, two role assignments, and a reader needs both.

`Embeddings` rides along as the vector-shaped output of the embed call
kind (000348).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from .identity import MechbenchPath
from .provenance import Provenance

# Base kinds, here so both halves of the platform agree on them.
BASE_KIND_AGENT = "~canonical/kinds/agent"
BASE_KIND_TRANSCRIPT = "~canonical/kinds/transcript"
BASE_KIND_EMBEDDINGS = "~canonical/kinds/embeddings"
BASE_KIND_CALL_PROVENANCE = "~canonical/kinds/call-provenance"

#: Providers that answer chat calls. `openai-compatible` is the generic
#: host (Together, Groq, DeepSeek, Mistral, OpenRouter, a self-hosted
#: vLLM or llama.cpp server); `mock` is the deterministic test provider
#: (task 000350), a real name because dry runs and cassettes record it.
EndpointProvider = Literal[
    "anthropic", "openai", "xai", "gemini", "fireworks",
    "openai-compatible", "mock",
]


class EndpointRef(BaseModel):
    """A model someone else runs. `provider_options` is keyed by
    provider name and passes through to the wire VERBATIM — cache
    control, thinking budgets, service tiers, anything the canonical
    fields do not name — so a protocol can always reach the real API,
    and what it asked for is recorded."""

    provider: EndpointProvider
    model: str = Field(..., min_length=1, description="The provider's own model id.")
    model_version: str | None = Field(
        None,
        description=(
            "The dated version pinned at seal, when one was pinned (task "
            "000352). Absent means 'whatever the alias resolves to', and the "
            "version that ANSWERED is recorded per call either way."
        ),
    )
    provider_options: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="provider name -> native fields merged after the canonical ones.",
    )


class Usage(BaseModel):
    """Tokens a call consumed. Cached input is reported separately
    because it is priced separately; it is NOT additional to
    `input_tokens`, it is part of it."""

    input_tokens: int = Field(0, ge=0)
    output_tokens: int = Field(0, ge=0)
    cache_read_tokens: int = Field(0, ge=0)
    cache_write_tokens: int = Field(0, ge=0)
    reasoning_tokens: int = Field(0, ge=0)


class CallProvenance(BaseModel):
    """One call to an external provider, as the item that carries it
    records it. The manifest sums these; a reader should be able to
    reconstruct the bill and the identity of what answered from the
    result alone."""

    kind: Literal["call_provenance"] = "call_provenance"
    provider: str
    model: str = Field(..., description="What was asked for.")
    model_version: str = Field(
        "", description="What answered — the provider's own dated string.")
    request_hash: str = Field(
        "",
        description=(
            "sha256 of the canonical request: what was ASKED, never how it "
            "was authenticated. The cassette key and the resume identity."
        ),
    )
    response_id: str = ""
    usage: Usage = Field(default_factory=Usage)
    cost_usd: float = Field(0.0, ge=0)
    priced: bool = Field(
        True,
        description="False when the model was not in the price table — a hole, not a guess.")
    price_table: str = Field("", description="Version of the price table that priced it.")
    tokens_exact: bool = Field(
        False,
        description="Whether the input count came from the provider's counter or an estimate.")
    latency_ms: int = Field(0, ge=0)
    attempts: int = Field(1, ge=1)
    throttled_seconds: float = Field(
        0.0, ge=0, description="Time spent waiting on rate limits, not on the model.")
    replayed: bool = Field(
        False, description="Answered from a cassette rather than the wire (task 000350).")
    provider_options: dict[str, Any] = Field(default_factory=dict)
    rate_limits: dict[str, Any] = Field(
        default_factory=dict, description="What the response headers said about quota.")


# --- participants and transcripts --------------------------------------------


class ToolSpec(BaseModel):
    """A tool as offered to a model: name, description, JSON Schema."""

    name: str = Field(..., min_length=1)
    description: str = ""
    input_schema: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}})


class ToolCall(BaseModel):
    """A model's request to run a tool. `id` correlates it with the
    result that answers it."""

    id: str = ""
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_call_id: str = ""
    content: str = ""
    is_error: bool = False


class Agent(BaseModel):
    """A participant in a conversation (task 000339): which model, what
    it was told, what it may call. An agent is a bench object so the
    same participant can be reused across protocols and compared
    against itself under one changed field."""

    kind: Literal["agent"] = "agent"
    name: str = Field(..., min_length=1, description="How the transcript refers to it.")
    model: EndpointRef | str = Field(
        ..., description="An endpoint, or a local model reference (repo[@rev]).")
    system: str = ""
    tools: list[ToolSpec] = Field(default_factory=list)
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int = Field(1024, gt=0)
    provider_options: dict[str, dict[str, Any]] = Field(default_factory=dict)
    #: Mandatory on remote participants — the api refuses a protocol
    #: whose remote node has no cap (task 000335).
    budget_usd: float | None = Field(None, gt=0)
    description: str = ""
    provenance: Provenance | None = None


class TranscriptMessage(BaseModel):
    """One turn. `participant` is who produced it; `role_as_seen` is
    the role it carried in the request that produced the NEXT turn —
    in a two-model conversation each side sees the other as the user,
    so one exchange has two role assignments and a reader needs both."""

    index: int = Field(..., ge=0)
    participant: str = Field(..., description="Agent name, or 'user' for scripted input.")
    role_as_seen: Literal["user", "assistant", "system"] = "assistant"
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    stop_reason: str = ""
    call: CallProvenance | None = Field(
        None, description="Absent for scripted turns: nobody was asked, nothing was spent.")


class Transcript(BaseModel):
    """What happened between participants (task 000339). One item of a
    conversation node's output; a document collection of these is what
    a hundred runs of the same conversation produce."""

    kind: Literal["transcript"] = "transcript"
    id: str = ""
    participants: list[str] = Field(
        default_factory=list, description="Agent names, in the order they first speak.")
    messages: list[TranscriptMessage] = Field(default_factory=list)
    stopped_because: str = Field(
        "", description="Turn policy's reason: 'max_turns', 'stop_phrase', 'tool_error', …")
    spend_usd: float = Field(0.0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance | None = None

    @model_validator(mode="after")
    def _messages_are_ordered(self) -> "Transcript":
        for i, m in enumerate(self.messages):
            if m.index != i:
                raise ValueError(
                    f"transcript messages must be indexed in order: message {i} "
                    f"declares index {m.index}")
        return self


class EmbeddingRow(BaseModel):
    id: str
    values: list[float] = Field(..., description="Flat vector; length must equal `dim`.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class Embeddings(BaseModel):
    """The embed call kind's output (task 000348): one row per input,
    flat vectors, the model that produced them recorded."""

    kind: Literal["embeddings"] = "embeddings"
    name: str = ""
    description: str = ""
    model: EndpointRef | str
    dim: int = Field(..., gt=0)
    rows: list[EmbeddingRow] = Field(default_factory=list)
    normalized: bool = Field(
        False, description="Whether rows are unit-length as returned.")
    spend_usd: float = Field(0.0, ge=0)
    provenance: Provenance | None = None

    @model_validator(mode="after")
    def _rows_match_dim(self) -> "Embeddings":
        wrong = [r.id for r in self.rows if len(r.values) != self.dim]
        if wrong:
            raise ValueError(
                f"embedding rows whose length is not dim={self.dim}: {wrong[:5]}")
        return self


class AgentCollection(BaseModel):
    """A named set of participants — what a conversation node binds in
    one edge instead of N."""

    kind: Literal["agent_collection"] = "agent_collection"
    name: str = ""
    description: str = ""
    agents: list[Agent] = Field(default_factory=list)
    provenance: Provenance | None = None


def endpoint_path(ref: EndpointRef) -> MechbenchPath:
    """A stable, readable identity for an endpoint — what a manifest
    prints and a catalog groups by."""
    return f"{ref.provider}:{ref.model}"
