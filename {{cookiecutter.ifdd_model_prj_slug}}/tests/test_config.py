"""Static checks of the web service of this instance.

They read the compose files and the nginx configuration as they are in this
repository and assert what the template promises. Docker is not needed; if
an nginx binary is installed, the configuration is also loaded and served by
nginx itself. tests/smoke.sh covers the running container.
"""

from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SERVICE = "model"
PREFIX = "IFDD_MODEL_"
COMPOSE_FILES = ["docker-compose-production.yml", "docker-compose-development.yml"]
NGINX_CONF = ROOT / "nginx" / "default.conf"
MIME_TYPES = ROOT / "nginx" / "mime.types"
EXAMPLES = ROOT / "src" / "linkml"


def load(path):
    return yaml.safe_load(Path(path).read_text())


def service(compose_file):
    return load(ROOT / compose_file)["services"][SERVICE]


def labels(compose_file):
    return service(compose_file)["labels"]


def nginx_conf():
    return NGINX_CONF.read_text()


def location_block(prefix):
    """The body of the first location block whose header starts with prefix."""
    text = nginx_conf()
    start = text.index(prefix)
    depth, begin = 0, text.index("{", start)
    for index in range(begin, len(text)):
        depth += {"{": 1, "}": -1}.get(text[index], 0)
        if depth == 0:
            return text[begin:index]
    raise AssertionError(f"unbalanced braces after {prefix!r}")


# --- compose -----------------------------------------------------------------

@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_compose_file_parses(compose_file):
    assert service(compose_file)["image"]


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_nothing_from_dotenv_reaches_the_container(compose_file):
    # .env only feeds the ${...} interpolation and just; nginx needs none of it.
    assert "env_file" not in service(compose_file)
    assert "environment" not in service(compose_file)


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_no_router_tls_or_entrypoint_labels(compose_file):
    # A router tls section replaces the TLS configuration of the proxy entry
    # point, Let's Encrypt resolver included; routers without entrypoints
    # attach to the default entry point. See the README of ifdd-de/proxy.
    for label in labels(compose_file):
        assert ".tls" not in label and ".entrypoints" not in label, label


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_router_and_service_share_one_name(compose_file):
    routers = {m.group(1) for label in labels(compose_file) if (m := re.match(r"traefik\.http\.routers\.([^.]+)\.", label))}
    services = {m.group(1) for label in labels(compose_file) if (m := re.match(r"traefik\.http\.services\.([^.]+)\.", label))}
    assert len(routers) == 1 and routers == services


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_host_rule_requires_the_host_variable(compose_file):
    rules = [label for label in labels(compose_file) if ".rule=" in label]
    assert rules and all(f"${{{PREFIX}HOST:?" in rule for rule in rules)


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_load_balancer_port_matches_nginx(compose_file):
    listen = re.search(r"^\s*listen\s+(\d+);", nginx_conf(), re.MULTILINE).group(1)
    ports = [label.split("=", 1)[1] for label in labels(compose_file) if "loadbalancer.server.port=" in label]
    assert ports == [listen]


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_docker_network_label_matches_the_external_network(compose_file):
    network = load(ROOT / compose_file)["networks"]["ext-proxy-net"]
    assert network["external"] is True
    assert f"traefik.docker.network={network['name']}" in labels(compose_file)


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_container_is_hardened(compose_file):
    svc = service(compose_file)
    assert svc["read_only"] is True
    assert "/tmp" in svc["tmpfs"]
    assert svc["cap_drop"] == ["ALL"]
    assert "no-new-privileges:true" in svc["security_opt"]


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_health_check_uses_the_health_endpoint(compose_file):
    assert "http://127.0.0.1:8080/healthz" in service(compose_file)["healthcheck"]["test"]
    assert "location = /healthz" in nginx_conf()


@pytest.mark.parametrize("compose_file", COMPOSE_FILES)
def test_configuration_is_mounted_read_only_and_exists(compose_file):
    volumes = service(compose_file)["volumes"]
    for source, target in (("./nginx/default.conf", "/etc/nginx/conf.d/default.conf"), ("./nginx/mime.types", "/etc/nginx/mime.types")):
        assert f"{source}:{target}:ro" in volumes
        assert (ROOT / source).is_file()


def content_volume(compose_file):
    volumes = [v for v in service(compose_file)["volumes"] if v.endswith(":/usr/share/nginx/html:ro")]
    assert len(volumes) == 1, "exactly one read-only content mount expected"
    return volumes[0]


def test_production_refuses_to_start_without_a_content_directory():
    assert content_volume("docker-compose-production.yml").startswith(f"${{{PREFIX}CONTENT_DIR:?")


def test_development_falls_back_to_the_examples():
    assert content_volume("docker-compose-development.yml").startswith(f"${{{PREFIX}CONTENT_DIR:-./src/linkml}}")
    assert EXAMPLES.is_dir()


def test_development_port_is_bound_to_loopback_only():
    assert all(port.startswith("127.0.0.1:") for port in service("docker-compose-development.yml")["ports"])


def test_production_publishes_no_port():
    assert "ports" not in service("docker-compose-production.yml")


# --- nginx ---------------------------------------------------------------------

def test_hidden_files_are_never_served():
    assert re.search(r"location ~ /\\\.\s*\{\s*return 404;\s*\}", nginx_conf())


def test_content_is_served_below_v1():
    assert re.search(r"alias /usr/share/nginx/html/;", location_block("location /v1/ "))
    assert re.search(r"location / \{\s*return 404;\s*\}", nginx_conf())


def test_cors_headers_are_sent_on_every_response():
    block = location_block("location /v1/ ")
    for header in ("Access-Control-Allow-Origin", "Access-Control-Allow-Methods", "Access-Control-Allow-Headers"):
        assert re.search(rf'add_header {header} "[^"]+" always;', block), header


def test_preflight_is_answered_without_content():
    assert re.search(r"if \(\$request_method = OPTIONS\)\s*\{\s*return 204;\s*\}", location_block("location /v1/ "))


def test_server_version_is_not_disclosed():
    assert re.search(r"^\s*server_tokens off;", nginx_conf(), re.MULTILINE)


def test_yaml_has_its_media_type():
    # RFC 9512 registers application/yaml.
    assert re.search(r"application/yaml\s+yaml yml;", MIME_TYPES.read_text())


def test_examples_are_yaml_files_in_type_and_unit():
    names = {p.parent.name for p in EXAMPLES.rglob("*.yaml")}
    assert names == {"type", "unit"}


# --- nginx itself, when installed -----------------------------------------------

NGINX = shutil.which("nginx") or (Path("/usr/sbin/nginx") if Path("/usr/sbin/nginx").exists() else None)


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main_conf(tmp_path, content, port):
    # Mirrors the http block of the unprivileged image closely enough for a
    # syntax and semantics check (includes, directives, contexts). The
    # server block is the instance's, with listen port and content directory
    # moved to the test.
    server = nginx_conf().replace("listen 8080;", f"listen 127.0.0.1:{port};")
    server = server.replace("alias /usr/share/nginx/html/;", f"alias {content}/;")
    (tmp_path / "server.conf").write_text(server)
    main = tmp_path / "nginx.conf"
    # As root, nginx runs its workers as nobody, who cannot read the
    # temporary directory of the test; the image runs everything as nginx.
    user = "user root;\n" if os.geteuid() == 0 else ""
    main.write_text(
        user
        + f"pid {tmp_path}/nginx.pid;\n"
        f"error_log {tmp_path}/error.log;\n"
        "daemon off;\n"
        "events {}\n"
        "http {\n"
        f"    include {MIME_TYPES};\n"
        "    default_type application/octet-stream;\n"
        f"    access_log {tmp_path}/access.log;\n"
        f"    client_body_temp_path {tmp_path}/client_temp;\n"
        f"    proxy_temp_path {tmp_path}/proxy_temp;\n"
        f"    fastcgi_temp_path {tmp_path}/fastcgi_temp;\n"
        f"    uwsgi_temp_path {tmp_path}/uwsgi_temp;\n"
        f"    scgi_temp_path {tmp_path}/scgi_temp;\n"
        "    sendfile on;\n"
        f"    include {tmp_path}/server.conf;\n"
        "}\n"
    )
    return main


@pytest.mark.skipif(NGINX is None, reason="no nginx binary installed")
def test_nginx_accepts_the_configuration(tmp_path):
    main = main_conf(tmp_path, EXAMPLES, free_port())
    result = subprocess.run([str(NGINX), "-t", "-q", "-e", str(tmp_path / "error.log"), "-p", str(tmp_path), "-c", str(main)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


@pytest.fixture
def served(tmp_path):
    """nginx with the configuration of this instance, serving a copy of the examples."""
    if NGINX is None:
        pytest.skip("no nginx binary installed")
    content = tmp_path / "content"
    shutil.copytree(EXAMPLES, content)
    (content / ".git").mkdir()
    (content / ".git" / "config").write_text("secret\n")
    port = free_port()
    main = main_conf(tmp_path, content, port)
    process = subprocess.Popen([str(NGINX), "-e", str(tmp_path / "error.log"), "-p", str(tmp_path), "-c", str(main)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            urllib.request.urlopen(base + "/healthz", timeout=1)
            break
        except OSError:
            time.sleep(0.1)
    yield base
    process.terminate()
    process.wait(timeout=10)


def get(url, method="GET"):
    request = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()


def test_served_source_is_the_file_with_the_yaml_type(served):
    status, headers, body = get(served + "/v1/type/product.yaml")
    assert status == 200
    assert headers["Content-Type"].split(";")[0] == "application/yaml"
    assert body == (EXAMPLES / "type" / "product.yaml").read_bytes()
    assert headers["Access-Control-Allow-Origin"]


def test_served_missing_file_is_404_with_cors(served):
    status, headers, _ = get(served + "/v1/type/does-not-exist.yaml")
    assert status == 404
    assert headers["Access-Control-Allow-Origin"]


def test_served_nothing_outside_v1(served):
    assert get(served + "/type/product.yaml")[0] == 404
    assert get(served + "/")[0] == 404


def test_served_hidden_files_are_404(served):
    assert get(served + "/v1/.git/config")[0] == 404


def test_served_preflight_is_204(served):
    assert get(served + "/v1/type/product.yaml", method="OPTIONS")[0] == 204
