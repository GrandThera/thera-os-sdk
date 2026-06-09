from __future__ import annotations

import json
from pathlib import Path
from typing import Any, BinaryIO

import httpx

from .errors import TheraOSAPIError
from .types import (
    AutoMethod,
    ForecastRunResponse,
    JsonDict,
    NRegimes,
    RegimeAnalyzeResponse,
    RegimeDashboardResponse,
    RegimeScopeResponse,
    SymbolicDatasetResponse,
    SymbolicFitResponse,
    SymbolicPredictResponse,
    SymbolicScenarioResponse,
    Term,
)

DEFAULT_BASE_URL = "https://api.thera-os.com/api/v1"


class TheraOSClient:
    """Synchronous client for the public Grand Thera AIT API."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
        api_key: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"User-Agent": "thera-os-python/0.1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout, headers=headers)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> TheraOSClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def health(self) -> JsonDict:
        return self._request("GET", "/../health")

    def forecast_run(
        self,
        *,
        series: list[float | None],
        steps: int = 100,
        simulations: int = 1000,
        targets: list[float] | None = None,
        drift_scale: float = 1.0,
        diffusion_scale: float = 1.0,
        mean_reversion: float = 0.18,
        rolling_window: int = 7,
    ) -> ForecastRunResponse:
        payload = {
            "series": series,
            "steps": steps,
            "simulations": simulations,
            "targets": targets,
            "drift_scale": drift_scale,
            "diffusion_scale": diffusion_scale,
            "mean_reversion": mean_reversion,
            "rolling_window": rolling_window,
        }
        return self._request("POST", "/forecast/run", json=payload)

    def forecast_upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        steps: int = 100,
        simulations: int = 1000,
        targets: list[float] | None = None,
        drift_scale: float = 1.0,
        diffusion_scale: float = 1.0,
        mean_reversion: float = 0.18,
        rolling_window: int = 7,
    ) -> ForecastRunResponse:
        data = {
            "steps": str(steps),
            "simulations": str(simulations),
            "targets": json.dumps(targets or []),
            "drift_scale": str(drift_scale),
            "diffusion_scale": str(diffusion_scale),
            "mean_reversion": str(mean_reversion),
            "rolling_window": str(rolling_window),
        }
        return self._upload("/forecast/upload", file, filename=filename, data=data)

    def regime_analyze(
        self,
        *,
        prices: list[float],
        dates: list[str] | None = None,
        window: int = 20,
        n_regimes: NRegimes = 3,
        auto_range: tuple[int, int] = (2, 5),
        auto_method: AutoMethod = "bic",
        max_iterations: int = 100,
        tolerance: float = 1e-6,
        markov_iterations: int = 100,
        markov_tolerance: float = 1e-5,
        min_markov_variance: float = 0.05,
    ) -> RegimeAnalyzeResponse:
        payload = {
            "prices": prices,
            "dates": dates,
            "window": window,
            "n_regimes": n_regimes,
            "auto_range": auto_range,
            "auto_method": auto_method,
            "max_iterations": max_iterations,
            "tolerance": tolerance,
            "markov_iterations": markov_iterations,
            "markov_tolerance": markov_tolerance,
            "min_markov_variance": min_markov_variance,
        }
        return self._request("POST", "/regime/analyze", json=payload)

    def regime_upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        window: int = 5,
        auto_method: AutoMethod = "bic",
        max_iterations: int = 100,
        tolerance: float = 1e-6,
        markov_iterations: int = 100,
        markov_tolerance: float = 1e-5,
        min_markov_variance: float = 0.05,
    ) -> RegimeDashboardResponse:
        data = {
            "window": str(window),
            "auto_method": auto_method,
            "max_iterations": str(max_iterations),
            "tolerance": str(tolerance),
            "markov_iterations": str(markov_iterations),
            "markov_tolerance": str(markov_tolerance),
            "min_markov_variance": str(min_markov_variance),
        }
        return self._upload("/regime/upload", file, filename=filename, data=data)

    def regime_scope(
        self,
        *,
        scenarios: dict[str, RegimeAnalyzeResponse],
        range_start: int,
        range_end: int,
        selected_index: int | None = None,
    ) -> RegimeScopeResponse:
        payload = {
            "scenarios": scenarios,
            "range_start": range_start,
            "range_end": range_end,
            "selected_index": selected_index,
        }
        return self._request("POST", "/regime/scope", json=payload)

    def symbolic_fit(
        self,
        *,
        data: list[dict[str, float | None]],
        dependent: str,
        independents: list[str],
        max_terms: int = 5,
    ) -> SymbolicFitResponse:
        payload = {
            "data": data,
            "dependent": dependent,
            "independents": independents,
            "max_terms": max_terms,
        }
        return self._request("POST", "/symbolic/fit", json=payload)

    def symbolic_upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        dependent: str | None = None,
        independents: list[str] | None = None,
    ) -> SymbolicDatasetResponse:
        data = {
            "dependent": dependent or "",
            "independents": json.dumps(independents) if independents is not None else "",
        }
        return self._upload("/symbolic/upload", file, filename=filename, data=data)

    def symbolic_fetch_dataset(
        self,
        *,
        url: str,
        dependent: str | None = None,
        independents: list[str] | None = None,
    ) -> SymbolicDatasetResponse:
        payload = {"url": url, "dependent": dependent, "independents": independents}
        return self._request("POST", "/symbolic/fetch-dataset", json=payload)

    def symbolic_predict(
        self,
        *,
        terms: list[Term],
        intercept: float,
        values: dict[str, float],
    ) -> SymbolicPredictResponse:
        payload = {"terms": terms, "intercept": intercept, "values": values}
        return self._request("POST", "/symbolic/predict", json=payload)

    def symbolic_scenario(
        self,
        *,
        terms: list[Term],
        intercept: float,
        values: dict[str, float],
        profiles: dict[str, dict[str, float]],
        independents: list[str],
        baseline: dict[str, float] | None = None,
        data: list[dict[str, float | None]] | None = None,
        forecast_steps: int = 12,
    ) -> SymbolicScenarioResponse:
        payload = {
            "terms": terms,
            "intercept": intercept,
            "values": values,
            "baseline": baseline,
            "profiles": profiles,
            "data": data or [],
            "independents": independents,
            "forecast_steps": forecast_steps,
        }
        return self._request("POST", "/symbolic/scenario", json=payload)

    def _request(self, method: str, path: str, **kwargs: Any) -> JsonDict:
        url = self._url(path)
        try:
            response = self._client.request(method, url, **kwargs)
        except httpx.HTTPError as exc:
            raise TheraOSAPIError(str(exc)) from exc
        if response.is_error:
            raise self._api_error(response)
        if not response.content:
            return {}
        return response.json()

    def _upload(
        self,
        path: str,
        file: str | Path | BinaryIO,
        *,
        filename: str | None,
        data: dict[str, str],
    ) -> JsonDict:
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            upload_name = filename or file_path.name
            with file_path.open("rb") as handle:
                files = {"file": (upload_name, handle)}
                return self._request("POST", path, data=data, files=files)

        upload_name = filename or getattr(file, "name", "upload.csv")
        files = {"file": (Path(str(upload_name)).name, file)}
        return self._request("POST", path, data=data, files=files)

    def _url(self, path: str) -> str:
        if path.startswith("/../"):
            root = self.base_url.rsplit("/api/v1", 1)[0]
            return f"{root}/{path.removeprefix('/../')}"
        return f"{self.base_url}/{path.lstrip('/')}"

    @staticmethod
    def _api_error(response: httpx.Response) -> TheraOSAPIError:
        try:
            body = response.json()
        except ValueError:
            body = response.text

        code: str | None = None
        message = response.reason_phrase
        if isinstance(body, dict):
            detail = body.get("detail")
            if isinstance(detail, dict):
                code = detail.get("code")
                message = str(detail.get("message") or message)
            elif detail:
                message = str(detail)
            elif body.get("message"):
                message = str(body["message"])

        return TheraOSAPIError(
            message,
            status_code=response.status_code,
            code=code,
            response_body=body,
        )
