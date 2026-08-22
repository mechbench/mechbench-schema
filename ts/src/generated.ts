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
 * Stable cluster identifier.
 */
export type Id = string;
/**
 * Human-readable cluster label (e.g. 'capital-city fact vectors'). Use empty string if the cluster is unlabeled.
 */
export type Label2 = string;
/**
 * Short description of how this direction was derived.
 */
export type Derivation = string;
/**
 * Explicit dimensionality, for validation and for headers that need the dimension without loading the full values array.
 */
export type Dim2 = number;
/**
 * Optional categorical label (e.g. 'capital-city', 'past-tense').
 */
export type Label3 = string | null;
export type Origin2 = "steering";
/**
 * Optional: the concept this steering vector is meant to push toward.
 */
export type TargetConcept = string | null;
/**
 * The vector's components. Length equals `dim`. Dtype is float on the wire; callers preserving bf16 should convert at the transport boundary.
 */
export type Values2 = number[];
/**
 * The classifier family the weight vector was fit for.
 */
export type ClassifierType = "linear" | "logistic" | "other";
/**
 * Explicit dimensionality, for validation and for headers that need the dimension without loading the full values array.
 */
export type Dim3 = number;
/**
 * Optional categorical label (e.g. 'capital-city', 'past-tense').
 */
export type Label4 = string | null;
export type Origin3 = "probe";
/**
 * What the probe predicts.
 */
export type TargetLabel = string;
/**
 * The vector's components. Length equals `dim`. Dtype is float on the wire; callers preserving bf16 should convert at the transport boundary.
 */
export type Values3 = number[];
/**
 * The member vectors, inline on the wire. Length should equal n_members (validated). For large clusters see task 000161 (binary transport) before scaling up.
 */
export type Members = (CapturedVector | SteeringVector | ProbeVector | CentroidVector)[];
/**
 * Explicit member count. Validated against len(members). Useful for header-only reads that don't want to materialize the full members list.
 */
export type NMembers1 = number;
/**
 * The member clusters.
 */
export type Clusters = Cluster[];
/**
 * Stable identifier for this cluster-set.
 */
export type Id1 = string;
/**
 * Human-readable label for the set.
 */
export type Label5 = string;
/**
 * Flat upper-triangle (excluding diagonal) of the centroid-cosine matrix. Length n*(n-1)/2 for n clusters. None if centroids are not present on all clusters.
 */
export type PairwiseCosine = number[] | null;
/**
 * Aggregate silhouette score across all member vectors. None if not computed.
 */
export type Silhouette = number | null;
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
export type Id2 = string;
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
 * ISO-8601 UTC timestamp, e.g. '2026-08-17T21:04:05Z'.
 */
export type CreatedAt = string;
/**
 * Recording granularity for document data. See module docstring for
 * the degradation-chain contract.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "Fidelity".
 */
export type Fidelity = "text" | "segments" | "trace";
/**
 * Paths of the objects this one was computed from.
 */
export type Inputs = string[];
/**
 * The operation that produced this object (task 000248) — a registered op path when one exists. Optional until the operation registry lands; recording it now prevents archaeology later.
 */
export type Operation = string | null;
/**
 * 'sha256:<hex>' fingerprint of the run configuration (fingerprint_params).
 */
export type ParamsFingerprint = string | null;
/**
 * Path of a stored params object (recoverable, unlike params_fingerprint which is only verifiable).
 */
export type ParamsRef = string | null;
/**
 * Producing package/script id, e.g. 'mechbench-compute'.
 */
export type Tool = string;
/**
 * Version or commit of the producing tool.
 */
export type Version = string;
/**
 * mechbench-schema version at write time.
 */
export type SchemaVersion = string;
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
 * Human-readable summary.
 */
export type Description3 = string;
/**
 * Stable script id, e.g. 'step_01_logit_lens_batch'.
 */
export type Experiment3 = string;
/**
 * Layer indices to be visually highlighted. Same semantics as the other domain-axis modules. Empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers3 = number[];
export type Kind4 = "logit_lens_trajectory";
/**
 * Log-probability of target_token under the lens at each (layer, position). Flat row-major, length n_layers * seq_len.
 */
export type Logprobs = number[];
/**
 * HuggingFace model id.
 */
export type Model3 = string;
/**
 * Total decoder-block count.
 */
export type NLayers3 = number;
/**
 * Identifier of the source prompt this record was computed against.
 */
export type PromptId1 = string;
/**
 * The raw prompt text.
 */
export type PromptText = string;
/**
 * Rank of target_token under the lens at each (layer, position). Flat row-major, length n_layers * seq_len. 0 == top-1.
 */
export type Ranks = number[];
/**
 * Input sequence length.
 */
export type SeqLen = number;
/**
 * The token whose rank and logprob are being tracked.
 */
export type TargetToken = string;
/**
 * Tokenizer-specific id of target_token.
 */
export type TargetTokenId1 = number;
/**
 * Optional per-position decoded tokens. Length equals seq_len when present. Useful for axis labelling. Absent when the positional labels aren't meaningful (e.g. for padding-heavy batched input).
 */
export type TokenLabels1 = string[] | null;
/**
 * Optional per-(layer, position) argmax token under the lens. Flat row-major when present, length n_layers * seq_len. Useful for narrating layer-by-layer condensation of the model's prediction.
 */
export type TopTokens = string[] | null;
/**
 * A mechbench object id. See mechbench/docs/IDENTITY_AND_NAMESPACING.md for the full grammar. Five categories: user-named (<owner>/<project>/.../<leaf>), canonical (~canonical/<area>/.../<leaf>), platform (~system/<area>/.../<leaf>), global content-hashed (~hash/<algo>:<digest>), and workspace-scoped content-hashed (<owner>/<project>/~hash/<algo>:<digest>).
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "MechbenchPath".
 */
export type MechbenchPath = string;
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PathCategory".
 */
export type PathCategory = "user_named" | "canonical" | "platform" | "global_hash" | "scoped_hash";
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
/**
 * HuggingFace model id.
 */
export type Model4 = string;
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
export type NLayers4 = number;
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerHeadData".
 */
export type PerHeadData = PerHeadScalarGrid;
/**
 * Human-readable summary.
 */
export type Description5 = string;
/**
 * Stable script id, e.g. 'step_32_per_head_dla'.
 */
export type Experiment5 = string;
/**
 * Layer indices to be visually highlighted. Same semantics as the per_layer_data.PerLayerBase field.
 */
export type GlobalLayers5 = number[];
export type Kind5 = "per_head_scalar_grid";
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
export type Model5 = string;
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
export type NLayers5 = number;
/**
 * Row-major [n_layers * n_heads] flat list. values[layer * n_heads + head] is the scalar for (layer, head).
 */
export type Values4 = number[];
/**
 * Human-readable summary; appears in chart footers.
 */
export type Description6 = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment6 = string;
/**
 * Layer indices to be visually highlighted. For Gemma 4 these are the global-attention layers; other architectures may use this for fresh-KV / MoE-routing / whatever architectural non-uniformity. Pass an empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers6 = number[];
/**
 * HuggingFace model id.
 */
export type Model6 = string;
/**
 * Total decoder-block count.
 */
export type NLayers6 = number;
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerLayerData".
 */
export type PerLayerData = LayerAblationPayload | DlaSweepPayload | ConvergencePayload;
/**
 * Human-readable summary.
 */
export type Description7 = string;
/**
 * Stable script id, e.g. 'step_01_logit_lens_batch'.
 */
export type Experiment7 = string;
/**
 * Layer indices to be visually highlighted. Same semantics as the other domain-axis modules. Empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers7 = number[];
/**
 * HuggingFace model id.
 */
export type Model7 = string;
/**
 * Total decoder-block count.
 */
export type NLayers7 = number;
/**
 * Identifier of the source prompt this record was computed against.
 */
export type PromptId2 = string;
/**
 * The raw prompt text.
 */
export type PromptText1 = string;
/**
 * Input sequence length.
 */
export type SeqLen1 = number;
/**
 * Optional per-position decoded tokens. Length equals seq_len when present. Useful for axis labelling. Absent when the positional labels aren't meaningful (e.g. for padding-heavy batched input).
 */
export type TokenLabels2 = string[] | null;
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerLayerPerPositionData".
 */
export type PerLayerPerPositionData = LogitLensTrajectory;
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
 * A named group of vectors with optional aggregate stats.
 *
 * `members` is stored inline for simplicity. `centroid` is optional —
 * computed on demand by callers that care; a Cluster with many members
 * but no centroid is a valid, useful record (the geometry analyses
 * often compute cluster membership without materializing a centroid).
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "Cluster".
 */
export interface Cluster {
  /**
   * Optional computed centroid. When present, its cluster_id should match this cluster's id (validated) and its n_members should match this cluster's n_members.
   */
  centroid?: CentroidVector | null;
  id: Id;
  label: Label2;
  members: Members;
  metadata?: Metadata4;
  n_members: NMembers1;
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
  dim: Dim2;
  label?: Label3;
  metadata?: Metadata2;
  origin?: Origin2;
  target_concept?: TargetConcept;
  values: Values2;
}
/**
 * Freeform string-keyed metadata for caller-specific extensions.
 */
export interface Metadata2 {
  [k: string]: string;
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
  dim: Dim3;
  label?: Label4;
  metadata?: Metadata3;
  origin?: Origin3;
  target_label: TargetLabel;
  values: Values3;
}
/**
 * Freeform string-keyed metadata for caller-specific extensions.
 */
export interface Metadata3 {
  [k: string]: string;
}
export interface Metadata4 {
  [k: string]: string;
}
/**
 * A collection of clusters plus cross-cluster aggregate stats.
 *
 * The pairwise-cosine matrix is stored as a flat upper-triangle list
 * (excluding the diagonal), length `n * (n - 1) / 2` for `n` clusters,
 * indexed row-major: entry `[i, j]` with `i < j` sits at index
 * `i * (n - 1) - (i * (i - 1)) // 2 + (j - i - 1)`. Callers that want
 * a square matrix reshape on ingest.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ClusterSet".
 */
export interface ClusterSet {
  clusters: Clusters;
  id: Id1;
  label?: Label5;
  metadata?: Metadata5;
  pairwise_cosine?: PairwiseCosine;
  silhouette?: Silhouette;
}
export interface Metadata5 {
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
  /**
   * Emission provenance (task 000237). Optional on read for records written before 0.9.0; the API requires it on new writes.
   */
  provenance?: Provenance | null;
}
/**
 * One source experiment's contribution to a cross-experiment summary.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ConvergenceRow".
 */
export interface ConvergenceRow {
  finding: Finding;
  id: Id2;
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
 * What produced an emitted object, from what, when.
 *
 * `created_at` is an ISO-8601 UTC timestamp string (e.g.
 * '2026-08-17T21:04:05Z'). `inputs` are the MechbenchPaths (including
 * `~hash/...` forms) of the objects this one was computed from — the
 * lineage index is derived from this list at emission time.
 * `params_fingerprint` comes from `fingerprint_params` over the run
 * config. `schema_version` records the mechbench-schema version the
 * object was written under.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "Provenance".
 */
export interface Provenance {
  created_at: CreatedAt;
  /**
   * Recording granularity, for document-bearing objects; None otherwise.
   */
  fidelity?: Fidelity | null;
  inputs?: Inputs;
  operation?: Operation;
  params_fingerprint?: ParamsFingerprint;
  params_ref?: ParamsRef;
  produced_by: ToolInfo;
  schema_version: SchemaVersion;
}
/**
 * The producing tool, pinned to a version.
 *
 * `tool` is a package or script identity (e.g. 'mechbench-compute');
 * `version` is its release or commit identifier. Together they are the
 * coarse code-fingerprint until 000162 introduces fine-grained ones.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ToolInfo".
 */
export interface ToolInfo {
  tool: Tool;
  version: Version;
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
  /**
   * Emission provenance (task 000237). Optional on read for records written before 0.9.0; the API requires it on new writes.
   */
  provenance?: Provenance | null;
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
  /**
   * Emission provenance (task 000237). Optional on read for records written before 0.9.0; the API requires it on new writes.
   */
  provenance?: Provenance | null;
}
/**
 * A logit-lens trajectory over layers and positions.
 *
 * Projects the residual stream at each (layer, position) through the
 * model's output head and records the target token's rank and
 * log-probability. Optionally records the argmax token at each
 * position ("top_tokens"), useful for narrating a trajectory.
 *
 * The three flat lists (`ranks`, `logprobs`, optionally `top_tokens`)
 * are all row-major `[n_layers * seq_len]`: index `layer * seq_len +
 * position`. Consumers reshape at ingest.
 *
 * Replaces the old records.LensStep + records.LensTrajectory pair,
 * which modeled one step per entry and paid struct-per-entry
 * overhead. The flat-list shape is tighter on the wire and matches
 * the convention used by the other per-layer and per-head modules.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "LogitLensTrajectory".
 */
export interface LogitLensTrajectory {
  description: Description3;
  experiment: Experiment3;
  global_layers: GlobalLayers3;
  kind?: Kind4;
  logprobs: Logprobs;
  model: Model3;
  n_layers: NLayers3;
  prompt_id: PromptId1;
  prompt_text: PromptText;
  ranks: Ranks;
  seq_len: SeqLen;
  target_token: TargetToken;
  target_token_id: TargetTokenId1;
  token_labels?: TokenLabels1;
  top_tokens?: TopTokens;
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
  description: Description4;
  experiment: Experiment4;
  global_layers: GlobalLayers4;
  model: Model4;
  n_heads: NHeads;
  n_kv_heads: NKvHeads;
  n_layers: NLayers4;
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
  description: Description5;
  experiment: Experiment5;
  global_layers: GlobalLayers5;
  kind?: Kind5;
  metric_name: MetricName1;
  metric_units: MetricUnits1;
  model: Model5;
  n_heads: NHeads1;
  n_kv_heads: NKvHeads1;
  n_layers: NLayers5;
  values: Values4;
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
  description: Description6;
  experiment: Experiment6;
  global_layers: GlobalLayers6;
  model: Model6;
  n_layers: NLayers6;
  /**
   * Emission provenance (task 000237). Optional on read for records written before 0.9.0; the API requires it on new writes.
   */
  provenance?: Provenance | null;
}
/**
 * Fields every per-(layer, position) record carries.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "PerLayerPerPositionBase".
 */
export interface PerLayerPerPositionBase {
  description: Description7;
  experiment: Experiment7;
  global_layers: GlobalLayers7;
  model: Model7;
  n_layers: NLayers7;
  prompt_id: PromptId2;
  prompt_text: PromptText1;
  seq_len: SeqLen1;
  token_labels?: TokenLabels2;
}
