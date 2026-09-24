from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from .identity import MechbenchPath
from .provenance import Provenance

BASE_KIND_AGENT = "~canonical/kinds/agent"
BASE_KIND_TRANSCRIPT = "~canonical/kinds/transcript"
BASE_KIND_EMBEDDINGS = "~canonical/kinds/embeddings"
BASE_KIND_CALL_PROVENANCE = "~canonical/kinds/call-provenance"

EndpointProvider = Literal[
    "anthropic", "openai", "xai", "gemini", "fireworks",
    "openai-compatible", "mock",
]


class EndpointRef(BaseModel):
    """A model someone else runs. `provider_options` is keyed by provider
    name and passed to that provider's API verbatim."""

    provider: EndpointProvider
    model: str = Field(..., min_length=1, description="The provider's own model id.")
    model_version: str | None = Field(
        None,
        description=(
            "The dated version pinned at seal, if any. Absent means whatever "
            "the alias resolves to; the version that answered is recorded "
            "per call either way."
        ),
    )
    provider_options: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="provider name -> native fields merged after the canonical ones.",
    )


class Usage(BaseModel):
    """Tokens a call consumed. Cached input is part of `input_tokens`, not
    additional to it."""

    input_tokens: int = Field(0, ge=0)
    output_tokens: int = Field(0, ge=0)
    cache_read_tokens: int = Field(0, ge=0)
    cache_write_tokens: int = Field(0, ge=0)
    reasoning_tokens: int = Field(0, ge=0)


class CallProvenance(BaseModel):
    """One call to an external provider: what was asked for, what answered,
    and what it cost."""

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
        False, description="Answered from a cassette rather than the wire.")
    provider_options: dict[str, Any] = Field(default_factory=dict)
    rate_limits: dict[str, Any] = Field(
        default_factory=dict, description="What the response headers said about quota.")


class ToolSpec(BaseModel):
    """A tool as offered to a model: name, description, JSON Schema."""

    name: str = Field(..., min_length=1)
    description: str = ""
    input_schema: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}})


class ToolCall(BaseModel):
    """A model's request to run a tool; `id` matches the result that
    answers it."""

    id: str = ""
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_call_id: str = ""
    content: str = ""
    is_error: bool = False


class Agent(BaseModel):
    """A conversation participant: a model, its system prompt, tools and
    sampling."""

    kind: Literal["text/agent", "agent"] = "text/agent"
    name: str = Field(..., min_length=1, description="How the transcript refers to it.")
    model: EndpointRef | str = Field(
        ..., description="An endpoint, or a local model reference (repo[@rev]).")
    system: str = ""
    tools: list[ToolSpec] = Field(default_factory=list)
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int = Field(1024, gt=0)
    provider_options: dict[str, dict[str, Any]] = Field(default_factory=dict)
    budget_usd: float | None = Field(None, gt=0)
    description: str = ""
    provenance: Provenance | None = None


class TranscriptMessage(BaseModel):
    """One turn. `participant` produced it; `role_as_seen` is the role it
    carried in the request for the next turn, since in a two-model
    conversation each side sees the other as the user."""

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
    """The messages exchanged between participants in one conversation."""

    kind: Literal["text/transcript", "transcript"] = "text/transcript"
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
    """Embedding vectors, one row per input. A legacy shape: new objects
    are a `collection` of `activations/vector`."""

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
    """A named set of conversation participants."""

    kind: Literal["agent_collection"] = "agent_collection"
    name: str = ""
    description: str = ""
    agents: list[Agent] = Field(default_factory=list)
    provenance: Provenance | None = None


def endpoint_path(ref: EndpointRef) -> MechbenchPath:
    return f"{ref.provider}:{ref.model}"
