from fastapi import APIRouter, FastAPI, status


def create_app() -> FastAPI:
    app = FastAPI(
        title="Injury Return-To-Play Tracker API",
        version="0.1.0",
        summary="Evidence tracking backend for staged return-to-play workflows.",
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {
            "service": "return-play-api",
            "status": "ok",
        }

    api_router = APIRouter(prefix="/api")

    @api_router.get("/athletes", status_code=status.HTTP_501_NOT_IMPLEMENTED)
    def list_athletes() -> dict[str, str]:
        return {"detail": "Athlete repository is not implemented yet."}

    @api_router.post("/athletes", status_code=status.HTTP_501_NOT_IMPLEMENTED)
    def create_athlete() -> dict[str, str]:
        return {"detail": "Athlete repository is not implemented yet."}

    @api_router.post("/injury-cases", status_code=status.HTTP_501_NOT_IMPLEMENTED)
    def create_injury_case() -> dict[str, str]:
        return {"detail": "Injury case repository is not implemented yet."}

    @api_router.get("/templates", status_code=status.HTTP_501_NOT_IMPLEMENTED)
    def list_templates() -> dict[str, str]:
        return {"detail": "Template repository is not implemented yet."}

    app.include_router(api_router)
    return app


app = create_app()
