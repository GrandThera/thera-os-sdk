from __future__ import annotations

from typing import Any, Literal, TypedDict

JsonDict = dict[str, Any]


class ParseDiagnostics(TypedDict, total=False):
    source: str
    column_label: str
    dimension: str
    total: int
    observed: int
    missing: int
    ranges: list[str]


class TargetProbability(TypedDict):
    target: float
    direction: Literal["above", "below"]
    probability_reached: float
    probability_final: float
    expected_overshoot: float


class ForecastHistogramBin(TypedDict):
    low: float
    high: float
    mid: float
    count: int


class ForecastTerminalSummary(TypedDict):
    p05: float
    p50: float
    p95: float
    spread: float
    min: float
    max: float
    sde_probability_reached: float
    sde_probability_final: float


class ForecastTerminalDistribution(TypedDict):
    bins: list[ForecastHistogramBin]
    smoothed_counts: list[float]
    max_count: float


class ForecastDensitySurface(TypedDict):
    timeline_indices: list[int]
    bins: list[ForecastHistogramBin]
    density: list[list[float]]
    max_density: float
    value_min: float
    value_max: float


class ForecastRunResponse(TypedDict, total=False):
    original: list[float | None]
    reconstructed: list[float]
    reconstruction_paths: list[list[float]]
    observed_mask: list[bool]
    missing_indices: list[int]
    drift: list[float]
    diffusion: list[float]
    forecast_mean: list[float]
    forecast_median: list[float]
    forecast_lower: list[float]
    forecast_upper: list[float]
    simulation_paths: list[list[float]]
    target_probabilities: list[TargetProbability]
    terminal_summary: ForecastTerminalSummary
    terminal_distribution: ForecastTerminalDistribution
    density_surface: ForecastDensitySurface
    steps: int
    simulations: int
    residual_scale: float
    train_loss: float
    parse_diagnostics: ParseDiagnostics | None


class RegimeCard(TypedDict, total=False):
    label: str
    value: str
    help: str
    level: float | None


class RegimeRow(TypedDict):
    index: int
    label: str
    probabilities: dict[str, float]
    filtered_probabilities: dict[str, float]
    viterbi_label: str
    uncertainty: float
    features: dict[str, float]
    cluster: int


class SurfacePoint(TypedDict):
    x: float
    y: float
    z: float


class VolatilitySurface(TypedDict):
    grid: list[list[SurfacePoint]]
    min_return: float
    max_return: float
    min_vol: float
    max_vol: float
    time_bins: int
    return_bins: int


class RegimeAnalyzeResponse(TypedDict, total=False):
    n_regimes: int
    rows: list[RegimeRow]
    transition_matrix: list[list[float]]
    viterbi_path: list[str]
    summary: dict[str, dict[str, float]]
    information_criteria: dict[str, float]
    selection_scores: dict[str, float]
    log_likelihoods: list[float]
    alerts: list[RegimeCard]
    selected_signals: list[RegimeCard]
    flow_diagnostics: list[RegimeCard]
    volatility_surface: VolatilitySurface | None


class RegimeDashboardResponse(TypedDict, total=False):
    prices: list[float]
    dates: list[str]
    scenarios: dict[str, RegimeAnalyzeResponse]
    default_scenario: str
    parse_diagnostics: ParseDiagnostics | None


class RegimeScopeResponse(TypedDict):
    scenarios: dict[str, RegimeAnalyzeResponse]
    range_start: int
    range_end: int


class SymbolicDatasetResponse(TypedDict):
    rows: list[dict[str, object]]
    columns: list[str]
    numeric_columns: list[str]
    dependent: str
    independents: list[str]
    profiles: dict[str, dict[str, float]]


class Term(TypedDict):
    expression: str
    latex: str
    coefficient: float


class Dependence(TypedDict):
    variable: str
    pearson_r: float
    abs_pearson: float
    mutual_information: float
    normalized_mi: float
    bins: int


class SymbolicMetrics(TypedDict):
    r2: float
    adjusted_r2: float
    rmse: float
    mae: float
    mape: float
    rss: float
    aic: float
    bic: float
    observations: int
    parameters: int


class SymbolicFitResponse(TypedDict):
    formula_latex: str
    terms: list[Term]
    intercept: float
    metrics: SymbolicMetrics
    dependence_diagnostics: list[Dependence]
    fitted_values: list[float]
    residuals: list[float]
    actual_values: list[float]
    term_values: list[list[float]]


class SymbolicPredictResponse(TypedDict):
    prediction: float


class SymbolicScenarioResponse(TypedDict):
    prediction: float
    baseline_prediction: float
    forecast: list[float]


NRegimes = int | Literal["auto"]
AutoMethod = Literal["silhouette", "aic", "bic", "icl"]
