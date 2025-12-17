from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

def setup_exception_handlers(app: FastAPI):
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        msg = str(exc).lower()

        if "not found" in msg:
            return JSONResponse(
                status_code=404,
                content={"detail": str(exc)}
            )

        if "not authorized" in msg or "forbidden" in msg:
            return JSONResponse(
                status_code=403,
                content={"detail": str(exc)}
            )

        if "already exists" in msg or "duplicate" in msg:
            return JSONResponse(
                status_code=409,
                content={"detail": str(exc)}
            )

        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
