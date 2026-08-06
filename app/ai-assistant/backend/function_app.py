import azure.functions as func
import json
import logging
import os
import uuid
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.cosmos import CosmosClient
from openai import AzureOpenAI

# ─── Configuration ──────────────────────────────────────────────────────────
OPENAI_ENDPOINT   = os.environ["AZURE_OPENAI_ENDPOINT"]
OPENAI_MODEL      = os.environ.get("AZURE_OPENAI_MODEL", "gpt-5.4-nano")
SEARCH_ENDPOINT   = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_INDEX      = os.environ.get("AZURE_SEARCH_INDEX", "devonboard-docs")
COSMOS_ENDPOINT   = os.environ["COSMOS_DB_ENDPOINT"]
COSMOS_DATABASE   = os.environ.get("COSMOS_DB_DATABASE", "db-ai-assistant")
COSMOS_CONTAINER  = os.environ.get("COSMOS_DB_CONTAINER", "chat_history")
HISTORY_WINDOW    = 6   # last 3 exchanges (6 messages) kept in context

SYSTEM_PROMPT = """You are DevOnboard AI, an intelligent onboarding assistant for the Azure AI Landing Zone platform.
You help engineers understand the Terraform IaC structure, Azure Cloud Adoption Framework (CAF) patterns,
subscription topology, CI/CD pipelines, and platform architecture.

Guidelines:
- Be concise, technical, and accurate.
- When relevant documentation is provided, base your answer on it and cite the source title.
- If you are unsure, say so clearly rather than guessing.
- Always use proper Azure resource naming conventions and Terraform HCL syntax when giving examples.
"""

# ─── CORS origins allowed ────────────────────────────────────────────────────
# Safety net: add CORS headers directly on every Function App response so it
# works whether traffic arrives via APIM or directly from the SWA.
ALLOWED_ORIGINS = [
    "https://apim-ht-ss-p-cin-01.azure-api.net",
]


def _cors_headers(origin: str | None = None) -> dict:
    """Return CORS headers. Allows any azurestaticapps.net or localhost origin."""
    allowed = origin if (
        origin and (
            origin.endswith(".azurestaticapps.net")
            or origin.startswith("http://localhost")
            or origin in ALLOWED_ORIGINS
        )
    ) else (origin or "*")

    return {
        "Access-Control-Allow-Origin":  allowed,
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, x-session-id",
        "Access-Control-Expose-Headers": "x-session-id",
        "Vary": "Origin",
    }


# ─── Azure Clients ───────────────────────────────────────────────────────────
_credential = DefaultAzureCredential()


def _openai_client() -> AzureOpenAI:
    token_provider = get_bearer_token_provider(
        _credential, "https://cognitiveservices.azure.com/.default"
    )
    return AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2025-01-01-preview",
    )


def _search_client() -> SearchClient:
    return SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=_credential,
    )


def _cosmos_container():
    client = CosmosClient(url=COSMOS_ENDPOINT, credential=_credential)
    db = client.get_database_client(COSMOS_DATABASE)
    return db.get_container_client(COSMOS_CONTAINER)


# ─── RAG: Retrieve context from AI Search ────────────────────────────────────
def retrieve_context(query: str, top_k: int = 4) -> str:
    """
    Perform a hybrid (keyword + semantic) search on the AI Search index.
    Falls back to simple keyword search if semantic is not configured.
    Returns a formatted context string for the system prompt.
    """
    try:
        search_client = _search_client()

        # Try semantic search first, fall back to simple on error
        try:
            results = search_client.search(
                search_text=query,
                top=top_k,
                query_type="semantic",
                semantic_configuration_name="default",
                select=["content", "title", "source"],
                query_caption="extractive",
            )
        except Exception:
            # Semantic not configured on index yet — use simple keyword search
            results = search_client.search(
                search_text=query,
                top=top_k,
                select=["content", "title", "source"],
            )

        chunks = []
        for r in results:
            title   = r.get("title") or r.get("source") or "Document"
            content = r.get("content", "").strip()
            if content:
                chunks.append(f"[{title}]\n{content}")

        if chunks:
            logging.info(f"Retrieved {len(chunks)} context chunks from AI Search.")
            return "\n\n---\n\n".join(chunks)

    except Exception as exc:
        logging.warning(f"AI Search retrieval skipped: {exc}")

    return ""


# ─── Cosmos DB: Session history ───────────────────────────────────────────────
def get_session_history(container, session_id: str) -> list[dict]:
    """Load the last HISTORY_WINDOW messages for the session from Cosmos DB."""
    try:
        query = (
            "SELECT c.role, c.content, c.timestamp "
            "FROM c "
            f"WHERE c.sessionId = '{session_id}' "
            "ORDER BY c.timestamp DESC "
            f"OFFSET 0 LIMIT {HISTORY_WINDOW}"
        )
        items = list(
            container.query_items(query=query, enable_cross_partition_query=False)
        )
        return [{"role": i["role"], "content": i["content"]} for i in reversed(items)]
    except Exception as exc:
        logging.warning(f"Cosmos DB history fetch skipped: {exc}")
        return []


def save_messages(container, session_id: str, user_msg: str, assistant_reply: str):
    """Persist user message and assistant reply to Cosmos DB."""
    ts = datetime.now(timezone.utc).isoformat()
    try:
        container.upsert_item({
            "id": str(uuid.uuid4()),
            "sessionId": session_id,
            "role": "user",
            "content": user_msg,
            "timestamp": ts,
        })
        container.upsert_item({
            "id": str(uuid.uuid4()),
            "sessionId": session_id,
            "role": "assistant",
            "content": assistant_reply,
            "timestamp": ts,
        })
    except Exception as exc:
        logging.warning(f"Cosmos DB save skipped: {exc}")


# ─── Function App Entry Point ─────────────────────────────────────────────────
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="chat", methods=["POST", "OPTIONS"])
def chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("DevOnboard AI /chat invoked.")
    origin = req.headers.get("Origin")
    cors   = _cors_headers(origin)

    # ── Handle CORS preflight ──────────────────────────────────────────────
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=cors)

    # ── Parse request ──────────────────────────────────────────────────────
    try:
        body = req.get_json()
    except ValueError:
        return _error_response("Invalid JSON body.", 400, cors)

    message    = (body.get("message") or "").strip()
    session_id = (body.get("session_id") or str(uuid.uuid4())).strip()

    if not message:
        return _error_response("'message' field is required.", 400, cors)

    try:
        # ── Step 1: RAG — retrieve relevant docs from AI Search ────────────
        context = retrieve_context(message)

        # ── Step 2: Session history from Cosmos DB ─────────────────────────
        cosmos = _cosmos_container()
        history = get_session_history(cosmos, session_id)

        # ── Step 3: Build prompt ───────────────────────────────────────────
        system_content = SYSTEM_PROMPT
        if context:
            system_content += f"\n\nRelevant platform documentation:\n\n{context}"

        messages = [{"role": "system", "content": system_content}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        # ── Step 4: Call Azure OpenAI ──────────────────────────────────────
        oai = _openai_client()
        completion = oai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.2,        # Low temp for consistent technical answers
            top_p=0.95,
        )
        reply = completion.choices[0].message.content.strip()

        # ── Step 5: Persist conversation to Cosmos DB ──────────────────────
        save_messages(cosmos, session_id, message, reply)

        logging.info(
            f"Chat complete. Model={OPENAI_MODEL} "
            f"Tokens={completion.usage.total_tokens if completion.usage else 'N/A'}"
        )

        response_headers = {**cors, "x-session-id": session_id}
        return func.HttpResponse(
            json.dumps({"reply": reply, "session_id": session_id}),
            status_code=200,
            mimetype="application/json",
            headers=response_headers,
        )

    except Exception as exc:
        logging.error(f"Unhandled error in /chat: {exc}", exc_info=True)
        return _error_response(
            f"Internal error ({type(exc).__name__}): {str(exc)}", 500, cors
        )


# ─── Health check ─────────────────────────────────────────────────────────────
@app.route(route="health", methods=["GET", "OPTIONS"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    origin = req.headers.get("Origin")
    cors   = _cors_headers(origin)
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=cors)
    return func.HttpResponse(
        json.dumps({"status": "healthy", "model": OPENAI_MODEL}),
        status_code=200,
        mimetype="application/json",
        headers=cors,
    )


# ─── Diagnostics endpoint ─────────────────────────────────────────────────────
@app.route(route="diagnostics", methods=["GET", "OPTIONS"])
def diagnostics(req: func.HttpRequest) -> func.HttpResponse:
    """
    Returns which required env vars are present (never exposes values).
    Useful for verifying Terraform app_settings were applied correctly.
    """
    origin = req.headers.get("Origin")
    cors   = _cors_headers(origin)
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=cors)

    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_MODEL",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_INDEX",
        "COSMOS_DB_ENDPOINT",
        "COSMOS_DB_DATABASE",
        "COSMOS_DB_CONTAINER",
    ]

    status = {
        var: ("✅ set" if os.environ.get(var) else "❌ MISSING")
        for var in required_vars
    }

    all_ok = all("✅" in v for v in status.values())

    payload = {
        "status":       "ok" if all_ok else "degraded",
        "model":        OPENAI_MODEL,
        "env_vars":     status,
        "missing_count": sum(1 for v in status.values() if "MISSING" in v),
    }

    logging.info(f"Diagnostics check: {payload['status']} — {payload['missing_count']} vars missing")

    return func.HttpResponse(
        json.dumps(payload, indent=2),
        status_code=200 if all_ok else 503,
        mimetype="application/json",
        headers=cors,
    )


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _error_response(message: str, status: int, cors: dict = None) -> func.HttpResponse:
    headers = cors or {}
    return func.HttpResponse(
        json.dumps({"error": message}),
        status_code=status,
        mimetype="application/json",
        headers=headers,
    )
