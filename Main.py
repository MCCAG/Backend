from fastapi import FastAPI

from Scripts.Lifespan import lifespan
from Scripts.Routers import generate_router

app = FastAPI(lifespan=lifespan)
app.include_router(generate_router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('Main:app', host='0.0.0.0', port=8080, reload=True)
