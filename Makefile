default:

.PHONY: now
now:
	@date

pdfs/nics_firearm_checks_-_month_year_by_state_type.pdf: now
	curl -s "https://www.fbi.gov/file-repository/nics_firearm_checks_-_month_year_by_state_type.pdf" > $@

data/nics-firearm-background-checks.csv: now
	python scripts/parse-pdf.py < pdfs/nics_firearm_checks_-_month_year_by_state_type.pdf > $@

charts: now
	python scripts/chart-total-checks-36-months.py < data/nics-firearm-background-checks.csv > charts/total-checks-36-months.png
	python scripts/chart-total-checks-all.py < data/nics-firearm-background-checks.csv > charts/total-checks-all.png

all: pdfs/nics_firearm_checks_-_month_year_by_state_type.pdf data/nics-firearm-background-checks.csv charts
