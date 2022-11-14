import multiprocessing
import time

import pytest
import uvicorn
from fastapi.testclient import TestClient

from src.main import app
from src.middlewares.black_list import BlackListHostMiddleware


def server(host, port):
    uvicorn.run(
        'conftest:app',
        host=host,
        port=port,
    )


@pytest.fixture(autouse=True, scope="session")
def start_server():
    p = multiprocessing.Process(target=server, args=('127.0.0.1', 8080))
    p.start()
    time.sleep(3)
    yield
    p.terminate()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def client_with_middleware():
    app.add_middleware(BlackListHostMiddleware, blocked_hosts=['*'])
    return TestClient(app)
