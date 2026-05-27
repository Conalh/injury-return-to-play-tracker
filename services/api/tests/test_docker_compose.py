from pathlib import Path


ROOT = Path(__file__).parents[3]


def test_compose_defines_local_production_stack() -> None:
    compose = (ROOT / "compose.yml").read_text()

    assert "db:" in compose
    assert "image: postgres:16-alpine" in compose
    assert "api:" in compose
    assert "context: ./services/api" in compose
    assert "web:" in compose
    assert "context: ./apps/web" in compose
    assert "RETURN_PLAY_DATABASE_URL: postgresql+psycopg://postgres:postgres@db:5432/return_play" in compose
    assert "alembic upgrade head" in compose
    assert "condition: service_healthy" in compose
    assert "pg_isready -U postgres -d return_play" in compose
    assert "seed-demo:" in compose
    assert 'command: ["python", "scripts/seed_demo.py"]' in compose


def test_api_and_web_dockerfiles_expose_health_checked_runtime() -> None:
    api_dockerfile = (ROOT / "services" / "api" / "Dockerfile").read_text()
    web_dockerfile = (ROOT / "apps" / "web" / "Dockerfile").read_text()

    assert "FROM python:3.11-slim" in api_dockerfile
    assert "python -m pip install --no-cache-dir ." in api_dockerfile
    assert 'CMD ["python", "-m", "uvicorn", "return_play.api:app"' in api_dockerfile
    assert "HEALTHCHECK" in api_dockerfile
    assert "http://127.0.0.1:8000/health" in api_dockerfile

    assert "FROM node:22-slim" in web_dockerfile
    assert "npm ci" in web_dockerfile
    assert "npm run build" in web_dockerfile
    assert 'CMD ["npx", "next", "start", "--hostname", "0.0.0.0", "--port", "3217"]' in web_dockerfile
    assert "HEALTHCHECK" in web_dockerfile
    assert "http://127.0.0.1:3217" in web_dockerfile


def test_alembic_and_runbook_support_compose_database_url() -> None:
    alembic_env = (ROOT / "services" / "api" / "alembic" / "env.py").read_text()
    runbook = (ROOT / "docs" / "operations" / "local-production-compose.md").read_text()

    assert "RETURN_PLAY_DATABASE_URL" in alembic_env
    assert "config.set_main_option(\"sqlalchemy.url\", database_url())" in alembic_env
    assert "docker compose up --build -d db api web" in runbook
    assert "docker compose --profile seed run --rm seed-demo" in runbook
    assert "docker compose down -v" in runbook


def test_ci_builds_compose_images_on_github_runner() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()

    assert "docker-compose-build:" in workflow
    assert "Docker compose build" in workflow
    assert "docker compose -f compose.yml config" in workflow
    assert "docker compose -f compose.yml build api web" in workflow
