.PHONY: analytics test run stop logs

analytics:
	python -m regional_insight.cli build

test:
	python -m pytest analytics/tests
	cd backend && ./gradlew test

run:
	docker compose up --build

stop:
	docker compose down

logs:
	docker compose logs -f api

