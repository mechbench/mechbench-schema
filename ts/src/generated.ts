// GENERATED FILE. Do not edit by hand.
// Re-run `python scripts/codegen.py` after changing the Pydantic source.

export type BaselineLogprob = number;
/**
 * Δ log p per ablated layer; length equals n_layers. More negative = more damaging.
 */
export type Damage = number[];
/**
 * The model's own top-1 prediction on this prompt.
 */
export type Target = string;
export type Text = string;
export type Top1Id = number;
/**
 * 0-indexed attention head within the layer.
 */
export type Head = number;
export type Kind = "attention_pattern";
/**
 * 0-indexed transformer layer.
 */
export type Layer = number;
/**
 * Key-side sequence length.
 */
export type NKeys = number;
/**
 * Query-side sequence length.
 */
export type NQueries = number;
/**
 * Optional per-position decoded tokens, for axis labelling. Assumes self-attention (same labels on both axes); if the shape is asymmetric, model the split explicitly.
 */
export type TokenLabels = string[] | null;
/**
 * Row-major flattened post-softmax weights, shape [n_queries * n_keys]. weights[q * n_keys + k] is the attention weight from query q to key k.
 */
export type Weights = number[];
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "AttentionTraceData".
 */
export type AttentionTraceData = AttentionPattern;
/**
 * Explicit dimensionality, for validation and for headers that need the dimension without loading the full values array.
 */
export type Dim = number;
/**
 * The hook-point class this capture came from. Distinguishes residual-stream vectors from branch-output vectors (attn_out, mlp_out, gate_out) captured at the same layer.
 */
export type HookKind = "resid_pre" | "resid_post" | "attn_out" | "mlp_out" | "gate_out" | "other";
/**
 * Fully qualified hook name, e.g. 'blocks.23.resid_post'.
 */
export type HookPoint = string;
/**
 * Optional categorical label (e.g. 'capital-city', 'past-tense').
 */
export type Label = string | null;
/**
 * 0-indexed transformer layer.
 */
export type Layer1 = number;
export type Origin = "captured";
/**
 * 0-indexed token position.
 */
export type Position = number;
/**
 * Identifier of the source prompt.
 */
export type PromptId = string;
/**
 * The vector's components. Length equals `dim`. Dtype is float on the wire; callers preserving bf16 should convert at the transport boundary.
 */
export type Values = number[];
/**
 * Stable id of the source cluster.
 */
export type ClusterId = string;
/**
 * Explicit dimensionality, for validation and for headers that need the dimension without loading the full values array.
 */
export type Dim1 = number;
/**
 * Optional categorical label (e.g. 'capital-city', 'past-tense').
 */
export type Label1 = string | null;
/**
 * Number of member vectors averaged into this centroid.
 */
export type NMembers = number;
export type Origin1 = "centroid";
/**
 * The vector's components. Length equals `dim`. Dtype is float on the wire; callers preserving bf16 should convert at the transport boundary.
 */
export type Values1 = number[];
/**
 * Human-readable summary; appears in chart footers.
 */
export type Description = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment = string;
/**
 * The findings-doc id (e.g. '04', '33').
 */
export type Finding = string;
/**
 * Stable experiment id.
 */
export type Id = string;
export type MetricName = string;
export type MetricUnits = string;
/**
 * One-paragraph description of the peak.
 */
export type PeakDescription = string;
/**
 * The layer this experiment most strongly fingerprinted.
 */
export type PeakLayer = number;
/**
 * Optional numeric peak value (metric-specific).
 */
export type PeakValue = number | null;
/**
 * The natural-language question the experiment answered.
 */
export type Question = string;
/**
 * Secondary layers worth marking on the chart; rendered as smaller markers. Pass an empty list if the experiment has a single peak.
 */
export type SecondLayers = number[];
/**
 * The script or artifact this row summarizes.
 */
export type Source = string;
/**
 * Human-readable title shown as the row label.
 */
export type Title = string;
export type Experiments = ConvergenceRow[];
/**
 * Layer indices to be visually highlighted. For Gemma 4 these are the global-attention layers; other architectures may use this for fresh-KV / MoE-routing / whatever architectural non-uniformity. Pass an empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers = number[];
export type Kind1 = "convergence";
/**
 * HuggingFace model id.
 */
export type Model = string;
/**
 * Total decoder-block count.
 */
export type NLayers = number;
/**
 * The layer the convergence centers on.
 */
export type PivotLayer = number;
/**
 * Prompt-set category tag (e.g. 'landmark', 'capital'). Pass an empty string when the prompt set has no categorical metadata.
 */
export type Category = string;
/**
 * (target − distractor) logit per layer; length equals n_layers.
 */
export type Diffs = number[];
export type Distractor = string;
export type DistractorTokenId = number;
export type Target1 = string;
export type TargetTokenId = number;
export type Text1 = string;
/**
 * Per-layer mean; length equals n_layers.
 */
export type Mean = number[];
/**
 * Per-layer median; length equals n_layers.
 */
export type Median = number[];
/**
 * Human-readable summary; appears in chart footers.
 */
export type Description1 = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment1 = string;
/**
 * Layer indices to be visually highlighted. For Gemma 4 these are the global-attention layers; other architectures may use this for fresh-KV / MoE-routing / whatever architectural non-uniformity. Pass an empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers1 = number[];
export type Kind2 = "dla_sweep";
/**
 * HuggingFace model id.
 */
export type Model1 = string;
/**
 * Total decoder-block count.
 */
export type NLayers1 = number;
export type Prompts = DlaPrompt[];
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "HookKind".
 */
export type HookKind1 = "resid_pre" | "resid_post" | "attn_out" | "mlp_out" | "gate_out" | "other";
/**
 * Human-readable summary; appears in chart footers.
 */
export type Description2 = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment2 = string;
/**
 * Layer indices to be visually highlighted. For Gemma 4 these are the global-attention layers; other architectures may use this for fresh-KV / MoE-routing / whatever architectural non-uniformity. Pass an empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers2 = number[];
export type Kind3 = "layer_ablation";
/**
 * HuggingFace model id.
 */
export type Model2 = string;
/**
 * Total decoder-block count.
 */
export type NLayers2 = number;
export type Prompts1 = AblationPrompt[];
/**
 * 0-indexed transformer layer.
 */
export type Layer2 = number;
/**
 * Log-probability of the target token at this (layer, position).
 */
export type Logprob = number;
/**
 * 0-indexed token position.
 */
export type Position1 = number;
/**
 * Rank of the target token under the lens readout.
 */
export type Rank = number;
/**
 * The model's argmax token under the lens at this (layer, position). Optional.
 */
export type TopToken = string | null;
/**
 * Identifier of the source prompt.
 */
export type PromptId1 = string;
export type Steps = LensStep[];
/**
 * The token whose rank/logprob is being tracked.
 */
export type TargetToken = string;
/**
 * Human-readable summary.
 */
export type Description3 = string;
/**
 * Stable script id, e.g. 'step_32_per_head_dla'.
 */
export type Experiment3 = string;
/**
 * Layer indices to be visually highlighted. Same semantics as the per_layer_data.PerLayerBase field.
 */
export type GlobalLayers3 = number[];
/**
 * HuggingFace model id.
 */
export type Model3 = string;
/**
 * Query-side attention heads per block.
 */
export type NHeads = number;
/**
 * KV-side attention heads per block (GQA).
 */
export type NKvHeads = number;
/**
 * Total decoder-block count.
 */
export type NLayers3 = number;
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerHeadData".
 */
export type PerHeadData = PerHeadScalarGrid;
/**
 * Human-readable summary.
 */
export type Description4 = string;
/**
 * Stable script id, e.g. 'step_32_per_head_dla'.
 */
export type Experiment4 = string;
/**
 * Layer indices to be visually highlighted. Same semantics as the per_layer_data.PerLayerBase field.
 */
export type GlobalLayers4 = number[];
export type Kind4 = "per_head_scalar_grid";
/**
 * What the scalars measure (e.g. 'DLA contribution').
 */
export type MetricName1 = string;
/**
 * Units for display (e.g. 'logit points'). Empty string if unitless.
 */
export type MetricUnits1 = string;
/**
 * HuggingFace model id.
 */
export type Model4 = string;
/**
 * Query-side attention heads per block.
 */
export type NHeads1 = number;
/**
 * KV-side attention heads per block (GQA).
 */
export type NKvHeads1 = number;
/**
 * Total decoder-block count.
 */
export type NLayers4 = number;
/**
 * Row-major [n_layers * n_heads] flat list. values[layer * n_heads + head] is the scalar for (layer, head).
 */
export type Values2 = number[];
/**
 * Human-readable summary; appears in chart footers.
 */
export type Description5 = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment5 = string;
/**
 * Layer indices to be visually highlighted. For Gemma 4 these are the global-attention layers; other architectures may use this for fresh-KV / MoE-routing / whatever architectural non-uniformity. Pass an empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers5 = number[];
/**
 * HuggingFace model id.
 */
export type Model5 = string;
/**
 * Total decoder-block count.
 */
export type NLayers5 = number;
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerLayerData".
 */
export type PerLayerData = LayerAblationPayload | DlaSweepPayload | ConvergencePayload;
/**
 * The classifier family the weight vector was fit for.
 */
export type ClassifierType = "linear" | "logistic" | "other";
/**
 * Explicit dimensionality, for validation and for headers that need the dimension without loading the full values array.
 */
export type Dim2 = number;
/**
 * Optional categorical label (e.g. 'capital-city', 'past-tense').
 */
export type Label2 = string | null;
export type Origin2 = "probe";
/**
 * What the probe predicts.
 */
export type TargetLabel = string;
/**
 * The vector's components. Length equals `dim`. Dtype is float on the wire; callers preserving bf16 should convert at the transport boundary.
 */
export type Values3 = number[];
/**
 * Short description of how this direction was derived.
 */
export type Derivation = string;
/**
 * Explicit dimensionality, for validation and for headers that need the dimension without loading the full values array.
 */
export type Dim3 = number;
/**
 * Optional categorical label (e.g. 'capital-city', 'past-tense').
 */
export type Label3 = string | null;
export type Origin3 = "steering";
/**
 * Optional: the concept this steering vector is meant to push toward.
 */
export type TargetConcept = string | null;
/**
 * The vector's components. Length equals `dim`. Dtype is float on the wire; callers preserving bf16 should convert at the transport boundary.
 */
export type Values4 = number[];
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "Vector".
 */
export type Vector = CapturedVector | SteeringVector | ProbeVector | CentroidVector;

export interface MechbenchSchema {
  [k: string]: unknown;
}
/**
 * One prompt's contribution to a per-layer ablation sweep.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "AblationPrompt".
 */
export interface AblationPrompt {
  baseline_logprob: BaselineLogprob;
  damage: Damage;
  target: Target;
  text: Text;
  top1_id: Top1Id;
}
/**
 * Post-softmax attention weights for one (layer, head) over a sequence.
 *
 * The weights matrix is stored as a flat row-major `[n_queries * n_keys]`
 * list. Consumers reshape on ingest; this keeps the wire format
 * JSON-native and trivially diffable. `token_labels`, when present,
 * labels both axes (self-attention) — for cross-attention the caller
 * should split into query_labels / key_labels (not yet modeled;
 * add when needed).
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "AttentionPattern".
 */
export interface AttentionPattern {
  head: Head;
  kind?: Kind;
  layer: Layer;
  n_keys: NKeys;
  n_queries: NQueries;
  token_labels?: TokenLabels;
  weights: Weights;
}
/**
 * A vector read from a hook point during a forward pass.
 *
 * Replaces the old `FactVectorRecord` from records.py. Adds the `origin`
 * discriminator and renames the old `kind` field to `hook_kind` to make
 * room for `origin` at the top level without collision.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "CapturedVector".
 */
export interface CapturedVector {
  dim: Dim;
  hook_kind?: HookKind;
  hook_point: HookPoint;
  label?: Label;
  layer: Layer1;
  metadata?: Metadata;
  origin?: Origin;
  position: Position;
  prompt_id: PromptId;
  values: Values;
}
/**
 * Freeform string-keyed metadata for caller-specific extensions.
 */
export interface Metadata {
  [k: string]: string;
}
/**
 * The centroid of a cluster of vectors.
 *
 * `cluster_id` is the stable id of the cluster this is the centroid of;
 * `n_members` is the size of that cluster at centroid-computation time.
 * Typically emitted alongside the Cluster record from cluster_data.py.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "CentroidVector".
 */
export interface CentroidVector {
  cluster_id: ClusterId;
  dim: Dim1;
  label?: Label1;
  metadata?: Metadata1;
  n_members: NMembers;
  origin?: Origin1;
  values: Values1;
}
/**
 * Freeform string-keyed metadata for caller-specific extensions.
 */
export interface Metadata1 {
  [k: string]: string;
}
/**
 * Cross-experiment summary: N source experiments, one peak layer each.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ConvergencePayload".
 */
export interface ConvergencePayload {
  description: Description;
  experiment: Experiment;
  experiments: Experiments;
  global_layers: GlobalLayers;
  kind?: Kind1;
  model: Model;
  n_layers: NLayers;
  pivot_layer: PivotLayer;
}
/**
 * One source experiment's contribution to a cross-experiment summary.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ConvergenceRow".
 */
export interface ConvergenceRow {
  finding: Finding;
  id: Id;
  metric_name: MetricName;
  metric_units?: MetricUnits;
  peak_description: PeakDescription;
  peak_layer: PeakLayer;
  peak_value?: PeakValue;
  question: Question;
  second_layers: SecondLayers;
  source: Source;
  title: Title;
}
/**
 * One prompt's contribution to a DLA sweep (target vs. distractor).
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "DlaPrompt".
 */
export interface DlaPrompt {
  category: Category;
  diffs: Diffs;
  distractor: Distractor;
  distractor_token_id: DistractorTokenId;
  target: Target1;
  target_token_id: TargetTokenId;
  text: Text1;
}
/**
 * step_33-shape: per-layer (target - distractor) DLA across a prompt battery.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "DlaSweepPayload".
 */
export interface DlaSweepPayload {
  aggregates: LayerAggregates;
  description: Description1;
  experiment: Experiment1;
  global_layers: GlobalLayers1;
  kind?: Kind2;
  model: Model1;
  n_layers: NLayers1;
  prompts: Prompts;
}
/**
 * Per-layer summary statistics across a prompt battery.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "LayerAggregates".
 */
export interface LayerAggregates {
  mean: Mean;
  median: Median;
}
/**
 * step_02-shape: per-layer ablation damage across a prompt battery.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "LayerAblationPayload".
 */
export interface LayerAblationPayload {
  aggregates: LayerAggregates;
  description: Description2;
  experiment: Experiment2;
  global_layers: GlobalLayers2;
  kind?: Kind3;
  model: Model2;
  n_layers: NLayers2;
  prompts: Prompts1;
}
/**
 * One (layer, position) entry of a logit-lens trajectory.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "LensStep".
 */
export interface LensStep {
  layer: Layer2;
  logprob: Logprob;
  position: Position1;
  rank: Rank;
  top_token?: TopToken;
}
/**
 * A logit-lens trajectory over layers and (optionally) positions.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "LensTrajectory".
 */
export interface LensTrajectory {
  metadata?: Metadata2;
  prompt_id: PromptId1;
  steps: Steps;
  target_token: TargetToken;
}
export interface Metadata2 {
  [k: string]: string;
}
/**
 * Fields every per-head data file carries.
 *
 * `n_heads` is the query-side head count per attention block;
 * `n_kv_heads` is the (smaller) KV-side count under grouped-query
 * attention. Charts rendering per-head data typically iterate the full
 * n_heads × n_layers grid; some downstream analyses care about the
 * KV-grouping (e.g. KV-sharing-boundary effects) and need n_kv_heads.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerHeadBase".
 */
export interface PerHeadBase {
  description: Description3;
  experiment: Experiment3;
  global_layers: GlobalLayers3;
  model: Model3;
  n_heads: NHeads;
  n_kv_heads: NKvHeads;
  n_layers: NLayers3;
}
/**
 * [n_layers × n_heads] grid of scalar values, one per head.
 *
 * Covers the common archetypes: per-head DLA contribution, OV-circuit
 * rank-0 singular value, attention entropy, Q/K silhouette, etc. The
 * `metric_name` and `metric_units` fields on the envelope describe what
 * the numbers *mean*; consumers render accordingly.
 *
 * The `values` field is stored as a flat row-major `[n_layers * n_heads]`
 * list of floats rather than a nested `list[list[float]]`. This keeps
 * the wire format JSON-native and trivially diffable; consumers reshape
 * on ingest.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerHeadScalarGrid".
 */
export interface PerHeadScalarGrid {
  description: Description4;
  experiment: Experiment4;
  global_layers: GlobalLayers4;
  kind?: Kind4;
  metric_name: MetricName1;
  metric_units: MetricUnits1;
  model: Model4;
  n_heads: NHeads1;
  n_kv_heads: NKvHeads1;
  n_layers: NLayers4;
  values: Values2;
}
/**
 * Fields every per-layer chart-data file carries.
 *
 * `experiment` is the stable id of the source script (matches the Python
 * module name). `model` is the HuggingFace model id. `n_layers` and
 * `global_layers` describe the model's layer structure so charts can
 * adapt across model variants (E4B: 42, E2B: 30, ...).
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerLayerBase".
 */
export interface PerLayerBase {
  description: Description5;
  experiment: Experiment5;
  global_layers: GlobalLayers5;
  model: Model5;
  n_layers: NLayers5;
}
/**
 * A linear-probe weight vector.
 *
 * Classifies residual-stream vectors by projecting onto this direction.
 * `target_label` names what the probe predicts; `classifier_type`
 * distinguishes linear regression, logistic regression, etc.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ProbeVector".
 */
export interface ProbeVector {
  classifier_type?: ClassifierType;
  dim: Dim2;
  label?: Label2;
  metadata?: Metadata3;
  origin?: Origin2;
  target_label: TargetLabel;
  values: Values3;
}
/**
 * Freeform string-keyed metadata for caller-specific extensions.
 */
export interface Metadata3 {
  [k: string]: string;
}
/**
 * A learned or derived direction intended for intervention.
 *
 * Carries a description of how it was derived — usually a short
 * natural-language note ("centroid of capital-city fact vectors minus
 * centroid of person-name fact vectors at L23.resid_post", or "SVD
 * component 0 of W_V for (L23, H5)"). Downstream consumers that need
 * to reproduce or compose steering vectors read the description.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "SteeringVector".
 */
export interface SteeringVector {
  derivation: Derivation;
  dim: Dim3;
  label?: Label3;
  metadata?: Metadata4;
  origin?: Origin3;
  target_concept?: TargetConcept;
  values: Values4;
}
/**
 * Freeform string-keyed metadata for caller-specific extensions.
 */
export interface Metadata4 {
  [k: string]: string;
}
