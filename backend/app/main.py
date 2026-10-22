from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.exclusions import router as exclusions_router
from app.api.routers.farmers import router as farmers_router
from app.api.routers.flags import router as flags_router
from app.api.routers.matches import router as matches_router
from app.api.routers.pipeline import router as pipeline_router
from app.api.routers.recommendations import router as recommendations_router
from app.api.routers.reports import router as reports_router

app = FastAPI(title="Agri Beneficiary Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(farmers_router)
app.include_router(pipeline_router)
app.include_router(flags_router)
app.include_router(matches_router)
app.include_router(recommendations_router)
app.include_router(reports_router)
app.include_router(exclusions_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
