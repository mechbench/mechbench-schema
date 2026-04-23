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
export type Head = number;
export type Layer = number;
export type NKeys = number;
export type NQueries = number;
/**
 * Optional per-position decoded tokens, for axis labelling.
 */
export type TokenLabels = string[] | null;
export type Weights = number[];
/**
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ChartData".
 */
export type ChartData = LayerAblationPayload | DlaSweepPayload | ConvergencePayload;
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
export type Description = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment = string;
/**
 * Layer indices to be visually highlighted. For Gemma 4 these are the global-attention layers; other architectures may use this for fresh-KV / MoE-routing / whatever architectural non-uniformity. Pass an empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers = number[];
export type Kind = "layer_ablation";
/**
 * HuggingFace model id.
 */
export type Model = string;
/**
 * Total decoder-block count.
 */
export type NLayers = number;
export type Prompts = AblationPrompt[];
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
export type Kind1 = "dla_sweep";
/**
 * HuggingFace model id.
 */
export type Model1 = string;
/**
 * Total decoder-block count.
 */
export type NLayers1 = number;
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
export type Prompts1 = DlaPrompt[];
/**
 * Human-readable summary; appears in chart footers.
 */
export type Description2 = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment2 = string;
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
export type GlobalLayers2 = number[];
export type Kind2 = "convergence";
/**
 * HuggingFace model id.
 */
export type Model2 = string;
/**
 * Total decoder-block count.
 */
export type NLayers2 = number;
/**
 * The layer the convergence centers on.
 */
export type PivotLayer = number;
/**
 * The hook name where this vector was captured, e.g. 'blocks.23.resid_post'.
 */
export type HookPoint = string;
export type Kind3 = "residual" | "attn_out" | "mlp_out" | "gate_out" | "other";
/**
 * Optional categorical label, e.g. 'capital-city', 'past-tense'.
 */
export type Label = string | null;
export type Layer1 = number;
export type Position = number;
export type PromptId = string;
export type Values = number[];
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
 * Human-readable summary; appears in chart footers.
 */
export type Description3 = string;
/**
 * Stable script id, e.g. 'step_02_layer_ablation'.
 */
export type Experiment3 = string;
/**
 * Layer indices to be visually highlighted. For Gemma 4 these are the global-attention layers; other architectures may use this for fresh-KV / MoE-routing / whatever architectural non-uniformity. Pass an empty list if the architecture has no layers worth highlighting.
 */
export type GlobalLayers3 = number[];
/**
 * HuggingFace model id.
 */
export type Model3 = string;
/**
 * Total decoder-block count.
 */
export type NLayers3 = number;

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
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "AttentionPattern".
 */
export interface AttentionPattern {
  head: Head;
  layer: Layer;
  n_keys: NKeys;
  n_queries: NQueries;
  token_labels?: TokenLabels;
  weights: Weights;
}
/**
 * step_02-shape: per-layer ablation damage across a prompt battery.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "LayerAblationPayload".
 */
export interface LayerAblationPayload {
  aggregates: LayerAggregates;
  description: Description;
  experiment: Experiment;
  global_layers: GlobalLayers;
  kind?: Kind;
  model: Model;
  n_layers: NLayers;
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
  kind?: Kind1;
  model: Model1;
  n_layers: NLayers1;
  prompts: Prompts1;
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
 * Cross-experiment summary: N source experiments, one peak layer each.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "ConvergencePayload".
 */
export interface ConvergencePayload {
  description: Description2;
  experiment: Experiment2;
  experiments: Experiments;
  global_layers: GlobalLayers2;
  kind?: Kind2;
  model: Model2;
  n_layers: NLayers2;
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
 * A single fact-vector observation.
 *
 * A fact vector is a residual-stream vector captured at a specific
 * (hook_point, prompt, position). It is the atomic unit of the geometry
 * analyses in mechbench-core.
 *
 * This interface was referenced by `MechbenchSchema`'s JSON-Schema
 * via the `definition` "FactVectorRecord".
 */
export interface FactVectorRecord {
  hook_point: HookPoint;
  kind?: Kind3;
  label?: Label;
  layer: Layer1;
  position: Position;
  prompt_id: PromptId;
  values: Values;
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
  metadata?: Metadata;
  prompt_id: PromptId1;
  steps: Steps;
  target_token: TargetToken;
}
export interface Metadata {
  [k: string]: string;
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
  description: Description3;
  experiment: Experiment3;
  global_layers: GlobalLayers3;
  model: Model3;
  n_layers: NLayers3;
}
