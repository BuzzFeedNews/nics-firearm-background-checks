default:

.PHONY: now all update
now:
	@date

all: pdfs/nics-checks-archive.pdf data/partial/nics-checks-archive.csv pdfs/nics-checks-last-five-years.pdf data/partial/nics-checks-last-five-years.csv data/nics-firearm-background-checks.csv charts

update: pdfs/nics-checks-last-five-years.pdf data/partial/nics-checks-last-five-years.csv data/nics-firearm-background-checks.csv charts

pdfs/nics-checks-archive.pdf: now
	wget "https://www.fbi.gov/file-repository/nics_firearms_checks_-_month_year_by_state_type-archive.pdf" -O $@

pdfs/nics-checks-last-five-years.pdf: now
	wget "https://www.fbi.gov/file-repository/nics_firearms_checks_-_month_year_by_state_type-last-5-years-1.pdf" -O $@

data/partial/nics-checks-archive.csv: now
	python scripts/parse-pdf.py pdfs/nics-checks-archive.pdf > $@

data/partial/nics-checks-last-five-years.csv: now
	python scripts/parse-pdf.py pdfs/nics-checks-last-five-years.pdf > $@

data/nics-firearm-background-checks.csv: now
	python scripts/combine-partials.py

charts: now
	python scripts/chart-total-checks-36-months.py < data/nics-firearm-background-checks.csv > charts/total-checks-36-months.png
	python scripts/chart-total-checks-all.py < data/nics-firearm-background-checks.csv > charts/total-checks-all.png

format:
	black scripts
	isort scripts --profile black

lint:
	black --check scripts
	isort --check scripts --profile black
	flake8 scripts --max-line-length 88
