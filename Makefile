lint:
\tpython -m ruff check .
\tpython -m ruff format --check .
\tpython -m mypy --config-file mypy.ini .

test:
\tpython -m pytest -m "not integration"

test-integration:
\tpython -m pytest -m "integration"
