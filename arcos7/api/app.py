from contextlib import asynccontextmanager

from fastapi import FastAPI

from arcos7.models.base import Base, engine
from arcos7.api.routers import artists, earnings, anomalies, claims, billing


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ARCOS7 Engine",
    version="2.0.0",
    description="Artist Earnings Accuracy Platform",
    lifespan=lifespan,
)

app.include_router(artists.router)
app.include_router(earnings.router)
app.include_router(anomalies.router)
app.include_router(claims.router)
app.include_router(billing.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
