from fastapi import FastAPI, Request, HTTPException
from loguru import logger
import hashlib
import hmac

from github_utils import create_pr


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


app = FastAPI()


@app.post("/webhook")
async def github_webhook(request: Request):
    # 验证请求来源 (可选)
    event = request.headers.get("X-GitHub-Event")
    logger.info(f"Received event: {event}")
    if event != "release":
        return "skip"
    payload = await request.json()
    # logger.info(f"Received payload: {payload}")
    assets = payload["release"]["assets"]
    create_pr(assets)
    return "success"


@app.get("/")
async def health_check():
    return {"message": "GitHub App is running!"}
