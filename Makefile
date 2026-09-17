.PHONY: all test demo deploy telemetry lint audit-iso9001 clean

all: test

test:
	python3 -m pytest -v

audit-iso9001:
	@echo "=== Verifying Somnia DreamDEX Agent Against ISO/DIS 9001:2026 Standards ==="
	python3 scripts/audit_iso9001_compliance.py

telemetry:
	python3 scripts/watch_testnet_events.py

demo:
	python3 scripts/record_demo_walkthrough.py

deploy:
	python3 scripts/deploy_somnia_testnet.py

lint:
	/Users/ishantpanchal/.local/bin/ruff check src/ tests/ scripts/

clean:
	rm -rf __pycache__ .pytest_cache target/
