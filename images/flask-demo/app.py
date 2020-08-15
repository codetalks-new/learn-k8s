import logging
import os
import socket
from flask import Flask, request, has_request_context

import time

from logging.config import dictConfig

from flask.wrappers import Response
from flask.json import JSONEncoder, jsonify, dumps


def get_env_as_dict():
    d = {}
    for key, value in os.environ.items():
        d[key] = value
    return d


class SilentJSONEncoder(JSONEncoder):
    def default(self, o: any):
        try:
            if isinstance(o, bytes):
                return o.decode("utf-8")
            return super().default(o)
        except TypeError:
            # if hasattr(o, "__dict__"):
            # return str(o.__dict__)
            return str(o)


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s[%(processName)s/%(threadName)s]: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


app = Flask(__name__)

logger = logging.root
logger.setLevel(logging.DEBUG)

app.config.update(JSON_AS_ASCII=False,)
app.json_encoder = SilentJSONEncoder


@app.before_request
def before_req():
    request.start_ms = int(time.time() * 1000)
    logger.info("%s %s %s", request.remote_addr, request.method, request.path)


@app.after_request
def after_req(resp: Response):
    ms = int(time.time() * 1000) - request.start_ms
    logger.info(
        "%s %s %s %d [%dms]",
        request.remote_addr,
        request.method,
        request.path,
        resp.status_code,
        ms,
    )
    return resp


@app.route("/")
def index():
    return "hello from canary"


@app.route("/echo")
def echo():
    data = request.__dict__
    data["env"] = get_env_as_dict()
    data["hostname"] = socket.gethostname()
    json_str = dumps(data, ensure_ascii=False, indent=2)
    return json_str


@app.route("/canary/on")
def canary_on():
    body = "turn on canary success"
    resp = Response(body)
    resp.set_cookie("canary", "on", max_age=1800, path="/", secure=False, httponly=True)
    return resp


@app.route("/canary/off")
def canary_off():
    body = "turn off canary success"
    resp = Response(body)
    resp.set_cookie("canary", "off", max_age=-1, path="/", secure=False, httponly=True)
    return resp


@app.route("/timeout")
def timeout():
    time.sleep(60 * 30)


@app.route("/server_error")
def server_error():
    raise Exception("inner error")


@app.route("/ping")
def ping():
    return "PONG"
