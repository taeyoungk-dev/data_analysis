.PHONY: analytics train lint test e2e check run stop logs

analytics:
	python -m regional_insight.cli build

train:
	python -m regional_insight.cli train

lint:
	ruff check analytics e2e

test:
	python -m pytest analytics/tests
	cd backend && ./gradlew test

e2e:
	python -m pytest e2e

check: lint test e2e

run:
	docker compose up --build

stop:
	docker compose down

logs:
	docker compose logs -f api
