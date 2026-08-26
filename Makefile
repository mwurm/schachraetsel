.PHONY: pdf test

pdf:
	PYTHONPATH=src python -m matt_in_1_pdf.cli -o examples/matt_in_1_beispiel.pdf

test:
	PYTHONPATH=src pytest -q
