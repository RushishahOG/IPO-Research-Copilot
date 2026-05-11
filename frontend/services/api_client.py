import requests
import time
from frontend.utils.constants import API_BASE_URL, MAX_RETRIES, TIMEOUT_SECONDS


class APIClientError(Exception):
    pass


def _request(method: str, endpoint: str, **kwargs) -> dict:
    url = f"{API_BASE_URL}{endpoint}"
    kwargs.setdefault("timeout", TIMEOUT_SECONDS)
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            last_error = "Cannot connect to backend. Ensure the API server is running."
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
        except requests.exceptions.Timeout:
            last_error = "Request timed out. Please try again."
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.5)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            if status == 404:
                raise APIClientError(f"Resource not found: {detail}")
            if status == 422:
                raise APIClientError(f"Validation error: {detail}")
            raise APIClientError(f"Error {status}: {detail}")
        except requests.exceptions.RequestException as e:
            last_error = f"Request failed: {e}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.5)
    raise APIClientError(last_error or "Request failed after multiple attempts")


def health_check() -> dict:
    try:
        return _request("GET", "/health")
    except APIClientError:
        return {"status": "unhealthy"}


def get_documents() -> list:
    try:
        data = _request("GET", "/documents")
        return data.get("documents", [])
    except APIClientError:
        return []


def upload_document(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        return _request("POST", "/upload", files={"file": f})


def delete_document(doc_name: str) -> dict:
    return _request("DELETE", f"/documents/{doc_name}")


def reingest_document(doc_name: str) -> dict:
    return _request("POST", f"/reingest/{doc_name}")


def chat_with_document(query: str, doc_name: str) -> dict:
    return _request(
        "POST",
        "/chat",
        json={"query": query, "doc_name": doc_name},
    )
