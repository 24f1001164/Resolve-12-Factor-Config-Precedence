import os
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Defaults
# -----------------------
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def parse_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)
    elif key == "debug":
        return parse_bool(value)
    else:
        return str(value)


def load_yaml():
    filename = "config.development.yaml"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def load_dotenv_layer():
    cfg = {}

    if os.getenv("APP_LOG_LEVEL") is not None:
        cfg["log_level"] = os.getenv("APP_LOG_LEVEL")

    # Alias
    if os.getenv("NUM_WORKERS") is not None:
        cfg["workers"] = os.getenv("NUM_WORKERS")

    return cfg


def load_os_env():
    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    cfg = {}

    for env_name, key in mapping.items():
        if env_name in os.environ:
            cfg[key] = os.environ[env_name]

    return cfg


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    config = DEFAULTS.copy()

    # YAML layer
    for k, v in load_yaml().items():
        config[k] = v

    # .env layer
    for k, v in load_dotenv_layer().items():
        config[k] = v

    # OS env layer
    for k, v in load_os_env().items():
        config[k] = v

    # CLI overrides
    for item in set:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        config[key] = value

    # Type coercion
    result = {}
    for k, v in config.items():
        result[k] = coerce(k, v)

    # Secret masking
    result["api_key"] = "****"

    return result
