from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["root"])

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "index.html"


@lru_cache
def _load_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def read_root(request: Request):
    base_url = str(request.base_url).rstrip("/")
    docs_url = f"{base_url}/docs"
    github_url = "https://github.com/MehdiKhoshnevisz/task-habit-api"

    return (
        _load_template()
        .replace("{{docs_url}}", docs_url)
        .replace("{{github_url}}", github_url)
    )
