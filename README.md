# thera-os

Python client for the public Grand Thera AIT API.

The package wraps the public API endpoints for:

- Neural SDE forecast: `POST /api/v1/forecast/run`
- Regime analysis: `POST /api/v1/regime/analyze`
- Regime dashboard scope: `POST /api/v1/regime/scope`
- Symbolic regression: `POST /api/v1/symbolic/fit`
- Symbolic prediction and scenarios
- Dataset/file upload endpoints

## Install

```bash
pip install thera-os
```

For local development:

```bash
git clone https://github.com/GrandThera/thera-os-python.git
cd thera-os-python
python -m pip install -e ".[dev]"
pytest
```

## Quick Start

```python
from thera_os import TheraOSClient

client = TheraOSClient()

prices = [5.12, 5.15, 5.11, 5.18, 5.21]

forecast = client.forecast_run(
    series=prices,
    steps=30,
    simulations=500,
    targets=[prices[-1] * 1.05],
)

regime = client.regime_analyze(
    prices=prices,
    window=2,
    n_regimes=2,
)

print(forecast["terminal_summary"])
print(regime["summary"])
```

By default the client uses:

```python
https://api.thera-os.com/api/v1
```

Use another deployment by passing `base_url`:

```python
client = TheraOSClient(base_url="http://localhost:8000/api/v1")
```

## Upload Examples

```python
from thera_os import TheraOSClient

client = TheraOSClient()

forecast = client.forecast_upload(
    "usdbrl.csv",
    steps=30,
    simulations=1000,
    targets=[5.60],
)

dataset = client.symbolic_upload(
    "dataset.xlsx",
    dependent="target",
    independents=["x1", "x2"],
)
```

## Error Handling

```python
from thera_os import TheraOSAPIError, TheraOSClient

client = TheraOSClient()

try:
    result = client.forecast_run(series=[1.0, 1.1, 1.2])
except TheraOSAPIError as exc:
    print(exc.status_code)
    print(exc.code)
    print(exc.message)
```

## Publishing Checklist

1. Create a public GitHub repository, for example `GrandThera/thera-os-python`.
2. Update the URLs in `pyproject.toml` if the repository name changes.
3. Confirm no private URLs, credentials, notebooks with secrets, `.venv`, `.git`, caches, or backend internals are committed.
4. Run:

```bash
python -m pip install -e ".[dev]"
pytest
python -m build
```

5. Publish when ready:

```bash
python -m twine upload dist/*
```

## License

MIT
