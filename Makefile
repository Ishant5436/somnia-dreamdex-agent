.PHONY: all test demo deploy telemetry lint clean

all: test

test:
	python3 -m pytest -v

telemetry:
	python3 scripts/watch_testnet_events.py

demo:
	python3 scripts/record_demo_walkthrough.py

deploy:
	python3 scripts/deploy_somnia_testnet.py

lint:
	python3 -m flake8 src/ tests/ --count --max-line-length=120 --statistics || true

clean:
	rm -rf __pycache__ .pytest_cache
