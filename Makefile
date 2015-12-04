default:

.PHONY: now
now:
	@date

pdfs/nics_firearm_checks_-_month_year_by_state_type.pdf: now
	curl -s "https://www.fbi.gov/about-us/cjis/nics/reports/nics_firearm_checks_-_month_year_by_state_type.pdf" > $@

data/nics-firearm-background-checks.csv: now
	python scripts/parse-pdf.py < pdfs/nics_firearm_checks_-_month_year_by_state_type.pdf > $@
