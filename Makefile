.PHONY: pdf test

pdf:
	PYTHONPATH=src python -m lichess_puzzle_pdf --output examples/preview.pdf

test:
	PYTHONPATH=src python -m pytest -q
