#!/usr/bin/env python3
"""Delegate local specialist tasks through authenticated native CLIs."""

import argparse
import fcntl
import json
import os
import re
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADVISORY = {"architecture-guardian", "principal-engineer"}
API_OVERRIDES = {
    "codex": ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL"),
    "claude": ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_PROFILE",
               "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
               "ANTHROPIC_BASE_URL"),
}
MAX_OUTPUT = 2 * 1024 * 1024
MAX_TASK = 64 * 1024
CLAUDE_DIRECTORY = ".claude"
TASK_TIMEOUT_MESSAGE = "Native CLI task timed out; its process group was stopped."


class DispatchError(Exception):
    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def validate_route(name, route):
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name) or not isinstance(route, dict):
        raise DispatchError("Routing contains an invalid specialist definition.")
    if route.get("harness") not in ("codex", "claude", "opencode"):
        raise DispatchError("Routing harness must be codex, claude or opencode.")
    model = route.get("model", "")
    if not isinstance(model, str) or (model and not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_./:#-]*", model)):
        raise DispatchError("Routing model must be a native model identifier, not command arguments.")
    if set(route) - {"harness", "model", "subscription_confirmed", "credential_id"}:
        raise DispatchError("Routing contains unsupported specialist settings.")
    validate_attestation(route)


def validate_attestation(route):
    if "subscription_confirmed" in route and type(route["subscription_confirmed"]) is not bool:
        raise DispatchError("Subscription confirmation must be a boolean.")
    credential = route.get("credential_id")
    if credential is not None and (not isinstance(credential, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", credential)):
        raise DispatchError("Credential ID must be native non-secret metadata, not a credential value.")
    if route["harness"] != "opencode" and set(route) & {"subscription_confirmed", "credential_id"}:
        raise DispatchError("Subscription attestation fields apply only to OpenCode routes.")


def routing(path):
    try:
        config = tomllib.loads(path.read_text())
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise DispatchError("Cannot read routing TOML; check --config.") from error
    agents = config.get("agents")
    if type(config.get("version")) is not int or config.get("version") != 1 or not isinstance(agents, dict) or not agents:
        raise DispatchError("Routing requires version = 1 and a non-empty agents table.")
    for name, route in agents.items():
        validate_route(name, route)
    return agents


def child_environment(harness):
    environment = dict(os.environ)
    for variable in API_OVERRIDES.get(harness, ()):
        environment.pop(variable, None)
    if harness == "claude":
        environment.pop("CLAUDECODE", None)
        if environment.get("CLAUDE_CONFIG_DIR"):
            environment["CLAUDE_CONFIG_DIR"] = os.path.abspath(environment["CLAUDE_CONFIG_DIR"])
    return environment


def executable(harness, environment):
    candidate = environment.get("WORKFORCE_" + harness.upper(), harness)
    found = shutil.which(candidate, path=environment.get("PATH", ""))
    if not found:
        raise DispatchError(f"{harness} executable not found; configure WORKFORCE_{harness.upper()} or PATH.")
    return os.path.abspath(found)


def metadata_command(command, environment, workspace=None):
    with tempfile.TemporaryDirectory(prefix="workforce-metadata-") as directory:
        job = Path(directory)
        write_handoff(job, "")
        output = run_child(command, environment, workspace, job, 15)
        errors = read_private_output(job / "stderr.txt")
    return subprocess.CompletedProcess(command, 0, output, errors)


def authenticate(harness, binary, environment, route=None, workspace=None):
    if harness == "opencode":
        return authenticate_opencode(binary, environment, route or {}, workspace)
    command = [binary, "login", "status"] if harness == "codex" else [binary, "auth", "status", "--json"]
    try:
        status = metadata_command(command, environment, workspace)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise DispatchError(f"Cannot check {harness} subscription login; use its native login command.") from error
    if harness == "codex":
        valid = status.returncode == 0 and "logged in using chatgpt" in (status.stdout + status.stderr).lower()
    else:
        try:
            login = json.loads(status.stdout)
            valid = (status.returncode == 0 and isinstance(login, dict) and login.get("loggedIn") is True
                     and login.get("authMethod") == "claude.ai" and login.get("apiProvider") == "firstParty")
        except ValueError:
            valid = False
    if not valid:
        raise DispatchError(f"{harness} subscription login required; no API-billing fallback is permitted.")
    return "subscription login verified"


def active_credential_matches(integration, provider, credential):
    if not isinstance(integration, dict) or integration.get("id") != provider:
        return False
    connections = integration.get("connections")
    if not isinstance(connections, list) or not connections or not isinstance(connections[0], dict):
        return False
    active = connections[0]
    return (active.get("type") == "credential" and active.get("id") == credential
            and active.get("method") in ("key", "oauth"))


def authenticate_opencode(binary, environment, route, workspace=None):
    model = route.get("model", "")
    if not route.get("subscription_confirmed") or not route.get("credential_id") or "/" not in model:
        raise DispatchError("OpenCode requires an explicit provider/model, cached credential ID and subscription_confirmed=true attestation; no billing fallback is permitted.")
    status = metadata_command([binary, "auth", "list", "--format", "json", "--standalone"], environment, workspace)
    try:
        integrations = json.loads(status.stdout)
    except ValueError as error:
        raise DispatchError("Cannot verify OpenCode cached authentication metadata.") from error
    provider = model.split("/", 1)[0]
    if status.returncode or not isinstance(integrations, list):
        raise DispatchError("Cannot verify OpenCode cached authentication metadata.")
    if any(active_credential_matches(integration, provider, route["credential_id"]) for integration in integrations):
        return "cached credential matches user-attested subscription; entitlement and spending are not verified"
    raise DispatchError("OpenCode active cached credential does not match the attested provider; reconnect using the native CLI.")


def verify_opencode_persona(binary, environment, workspace, name):
    status = metadata_command([binary, "debug", "agents"], environment, workspace)
    try:
        agents = json.loads(status.stdout)
    except ValueError as error:
        raise DispatchError("Cannot verify effective OpenCode specialist metadata; no agent fallback is permitted.") from error
    if status.returncode == 0 and isinstance(agents, list):
        for agent in agents:
            if isinstance(agent, dict) and agent.get("id") == name and agent.get("mode") in ("primary", "all"):
                return
    raise DispatchError("OpenCode specialist is unavailable for primary execution; configure its native mode explicitly. No agent fallback is permitted.")


def persona_path(name, harness):
    if harness == "codex":
        return ROOT / "roles" / "codex" / "files" / "agents" / (name + ".toml")
    if harness == "claude":
        directory = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / CLAUDE_DIRECTORY)))
    else:
        directory = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "opencode"
    return directory / "agents" / (name + ".md")


def check_claude_settings(workspace):
    directory = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / CLAUDE_DIRECTORY)))
    paths = [directory / "settings.json", directory / "settings.local.json",
             workspace / CLAUDE_DIRECTORY / "settings.json", workspace / CLAUDE_DIRECTORY / "settings.local.json",
             Path("/Library/Application Support/ClaudeCode/managed-settings.json")]
    for path in paths:
        if not path.is_file():
            continue
        try:
            settings = json.loads(path.read_text())
        except (OSError, ValueError) as error:
            raise DispatchError("Cannot verify Claude authentication settings; check native configuration.") from error
        if not isinstance(settings, dict) or settings.get("apiKeyHelper"):
            raise DispatchError("Claude API-key helpers are not permitted for subscription-only delegation.")


def require_persona(name, harness):
    path = persona_path(name, harness)
    if not path.is_file():
        raise DispatchError(f"Specialist persona missing for {harness}; deploy the corresponding client role first.")
    if harness == "codex":
        try:
            agent = tomllib.loads(path.read_text())
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
            raise DispatchError("Cannot read native Codex specialist persona.") from error
        if agent.get("name") != name or not isinstance(agent.get("developer_instructions"), str):
            raise DispatchError("Codex specialist persona has invalid metadata.")
        return agent["developer_instructions"].replace("~/.agents/skills/ai-agent-workforce/", "~/.skills/")
    return ""


def command_for(binary, name, route, write):
    validate_route(name, route)
    harness = route["harness"]
    if harness == "codex":
        command = [binary, "exec", "--sandbox", "workspace-write" if write else "read-only",
                   "--json", "--color", "never",
                   "-c", 'forced_login_method="chatgpt"', "-c", 'model_provider="openai"']
    elif harness == "claude":
        command = [binary, "--print", "--agent", name, "--output-format", "json",
                   "--permission-mode", "default" if write else "plan",
                   "--disallowedTools", "Agent,Task", "--settings",
                   json.dumps({"env": dict.fromkeys(API_OVERRIDES["claude"], ""),
                               "forceLoginMethod": "claudeai"})]
        if not write:
            command += ["--tools", "Read,Glob,Grep", "--strict-mcp-config",
                        "--mcp-config", '{"mcpServers":{}}']
    else:
        command = [binary, "run", "--agent", name, "--format", "json"]
    if route.get("model"):
        command += ["--model", route["model"]]
    if harness == "codex":
        command.append("-")
    return command


def private_directory(path):
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise DispatchError("Workspace handoff directory is not a regular directory.")
    path.mkdir(mode=0o700, exist_ok=True)


@contextmanager
def workspace_job(workspace):
    context = workspace / ".context"
    private_directory(context)
    runtime = context / "workforce"
    private_directory(runtime)
    if runtime.stat().st_mode & 0o077:
        raise DispatchError("Existing .context/workforce must have private permissions (0700).")
    descriptor = os.open(runtime / ".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        lock = os.fstat(descriptor)
        if not stat.S_ISREG(lock.st_mode) or lock.st_nlink != 1 or lock.st_mode & 0o077:
            raise DispatchError("Workspace lock must be a private regular file with a single link.")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise DispatchError("Another workforce task is running in this workspace; retry after it completes.") from error
        with tempfile.TemporaryDirectory(prefix="job-", dir=runtime) as directory:
            yield Path(directory)
    finally:
        os.close(descriptor)


def stop_process(process):
    if getattr(process, "_workforce_stopped", False):
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()
    process._workforce_stopped = True


def private_file(path):
    return os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), "wb")


def write_handoff(job, prompt, filename="input.txt"):
    if filename not in ("input.txt", "task.md"):
        raise DispatchError("Invalid private handoff filename.")
    with private_file(job / filename) as destination:
        destination.write(prompt.encode("utf-8"))


def read_private_output(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source:
        metadata = os.fstat(source.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise DispatchError("Native CLI output must be a regular file with a single link.")
        output = source.read(MAX_OUTPUT + 1)
    if len(output) > MAX_OUTPUT:
        raise DispatchError("Native CLI output exceeded the safety limit.")
    return output.decode("utf-8", errors="replace")


def collect_output(process, output, errors, timeout):
    deadline = time.monotonic() + timeout
    captured = 0
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ, output)
        selector.register(process.stderr, selectors.EVENT_READ, errors)
        while selector.get_map():
            if process.poll() is not None:
                stop_process(process)
            if time.monotonic() >= deadline:
                raise DispatchError(TASK_TIMEOUT_MESSAGE, 124)
            for event in selector.select(timeout=0.05):
                key = event[0]
                chunk = os.read(key.fd, min(65536, MAX_OUTPUT - captured + 1))
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                if captured + len(chunk) > MAX_OUTPUT:
                    raise DispatchError("Native CLI output exceeded the safety limit; its process group was stopped.")
                key.data.write(chunk)
                captured += len(chunk)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise DispatchError(TASK_TIMEOUT_MESSAGE, 124)
    try:
        process.wait(timeout=remaining)
    except subprocess.TimeoutExpired as error:
        raise DispatchError(TASK_TIMEOUT_MESSAGE, 124) from error


def run_child(command, environment, workspace, job, timeout):
    input_file = job / "input.txt"
    stdout_file, stderr_file = job / "stdout.jsonl", job / "stderr.txt"
    descriptor = os.open(input_file, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source, private_file(stdout_file) as output, private_file(stderr_file) as errors:
        metadata = os.fstat(source.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise DispatchError("Native CLI input must be a regular file.")
        process = subprocess.Popen(command, env=environment, cwd=workspace, stdin=source,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            collect_output(process, output, errors, timeout)
        finally:
            stop_process(process)
            process.stdout.close()
            process.stderr.close()
    if process.returncode:
        raise DispatchError(f"Native CLI exited with status {process.returncode}; check its login, model and permissions.")
    return read_private_output(stdout_file)


def result_events(output):
    try:
        document = json.loads(output)
        records = [document] if isinstance(document, dict) else []
    except ValueError:
        records = output.splitlines()
    for record in records:
        try:
            event = json.loads(record) if isinstance(record, str) else record
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") in ("error", "turn.failed") or event.get("is_error") is True:
            raise DispatchError("Native CLI reported a task failure; check its login, model and permissions.")
        yield event


def codex_result(output):
    response, completed = "", False
    for event in result_events(output):
        if event.get("type") == "turn.started":
            response, completed = "", False
        if event.get("type") == "turn.completed":
            completed = True
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            response = item["text"]
    if not completed or not response.strip():
        raise DispatchError("Native CLI returned no completed specialist response; no success is assumed.")
    return response.strip()


def result_text(harness, output):
    if harness == "codex":
        return codex_result(output)
    text = []
    for event in result_events(output):
        if harness == "claude" and event.get("type") == "result" and isinstance(event.get("result"), str):
            text.append(event["result"])
        if harness == "opencode" and event.get("type") == "text":
            part = event.get("part", {})
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                text.append(part["text"])
    result = "\n".join(text).strip()
    if not result:
        raise DispatchError("Native CLI returned no final specialist response; no success is assumed.")
    return result


def redact(text):
    for name, value in os.environ.items():
        if len(value) >= 8 and re.search(r"TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY", name, re.I):
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"-----BEGIN [^-\n]*PRIVATE KEY-----.*?-----END [^-\n]*PRIVATE KEY-----",
                  "[REDACTED PRIVATE KEY]", text, flags=re.S)
    text = re.sub(r"\bBearer\s+[a-z0-9._~+/-]+=*", "Bearer [REDACTED]", text, flags=re.I)
    text = re.sub(r"\b(?:sk-[\w-]{12,}|gh[pousr]_\w{20,})", "[REDACTED]", text, flags=re.ASCII)
    return text


def read_task(path):
    if path is not None:
        descriptor = os.open(path.expanduser(), os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise DispatchError("Task input must be a regular file.")
            payload = source.read(MAX_TASK + 1)
    else:
        if sys.stdin.isatty():
            raise DispatchError("Provide --task-file or pipe a task on stdin.")
        payload = sys.stdin.buffer.read(MAX_TASK + 1)
    if len(payload) > MAX_TASK:
        raise DispatchError("Task must be non-empty and at most 64 KiB.")
    try:
        task = payload.decode("utf-8")
    except UnicodeError as error:
        raise DispatchError("Task input must be UTF-8 text.") from error
    if not task.strip():
        raise DispatchError("Task must be non-empty and at most 64 KiB.")
    return task


def delegation_context(options, agents):
    name = next((name for name in agents if name == options.agent), None)
    if name is None:
        raise DispatchError("Unknown specialist; run workforce list.")
    if options.allow_write and name in ADVISORY:
        raise DispatchError("Architecture guardian and principal engineer are advisory; write access is refused.")
    workspace = options.workspace.expanduser().resolve()
    if not workspace.is_dir():
        raise DispatchError("Workspace must be an existing directory.")
    task = read_task(options.task_file)
    route = agents[name]
    harness = route["harness"]
    result = {"agent": name, "harness": harness, "model": route.get("model") or "configured-default",
              "workspace": str(workspace), "access": "workspace-write" if options.allow_write else "read-only"}
    return name, route, workspace, task, result


def dry_run_result(name, route, write, result):
    blocked = route["harness"] == "opencode" and (not write or not route.get("subscription_confirmed")
              or not route.get("credential_id") or "/" not in route.get("model", ""))
    return result | {"status": "dry-run", "blocked": blocked, "prerequisites": "not checked",
                     "command": command_for(route["harness"], name, route, write)}


def delegation_prerequisites(name, route, workspace, write):
    harness = route["harness"]
    if harness == "opencode" and not write:
        raise DispatchError("OpenCode read-only delegation is disabled: effective native restrictions are not verified. Use a read-only Codex/Claude route for reviews; do not grant writes to bypass this guard.")
    if os.environ.get("WORKFORCE_ACTIVE"):
        raise DispatchError("Recursive workforce delegation is refused; return control to the coordinator.")
    persona = require_persona(name, harness)
    environment = child_environment(harness)
    binary = executable(harness, environment)
    if harness == "claude":
        check_claude_settings(workspace)
    authenticate(harness, binary, environment, route, workspace)
    if harness == "opencode":
        verify_opencode_persona(binary, environment, workspace, name)
    environment["WORKFORCE_ACTIVE"] = "1"
    git_binary = shutil.which("git", path=environment.get("PATH", ""))
    if not git_binary:
        raise DispatchError("Git is required to validate the workspace.")
    checked = subprocess.run([os.path.abspath(git_binary), "rev-parse", "--show-toplevel"], cwd=workspace,
                             capture_output=True, text=True, timeout=10)
    if checked.returncode:
        raise DispatchError("Delegation requires a Git workspace.")
    worktree = Path(checked.stdout.strip()).resolve()
    if harness == "claude" and worktree != workspace:
        check_claude_settings(worktree)
    return persona, environment, binary, worktree


def delegation_prompt(name, persona, task):
    prompt = (f"You are handling a delegated {name} task. Complete only this task and return your findings. "
              "Do not recursively delegate through workforce. Do not commit, push or deploy. "
              "Never include secrets, tokens, private keys or sensitive payloads in your response.\n\n")
    if persona:
        prompt += "Specialist operating instructions:\n" + persona + "\n\n"
    prompt += "Coordinator task:\n" + task
    return prompt


def attach_opencode_task(command, binary, environment, workspace, job, prompt):
    help_result = metadata_command([binary, "run", "--help"], environment, workspace)
    if help_result.returncode:
        raise DispatchError("Cannot inspect OpenCode run capabilities.")
    if "--standalone" in help_result.stdout:
        command.append("--standalone")
    write_handoff(job, prompt, "task.md")
    command += ["--file", str(job / "task.md"), "Complete the delegated task in the attached file."]


def delegate(options, agents):
    name, route, workspace, task, result = delegation_context(options, agents)
    if options.dry_run:
        return dry_run_result(name, route, options.allow_write, result)
    persona, environment, binary, worktree = delegation_prerequisites(name, route, workspace, options.allow_write)
    harness = route["harness"]
    prompt = delegation_prompt(name, persona, task)
    with workspace_job(worktree) as job:
        command = command_for(binary, name, route, options.allow_write)
        if harness == "opencode":
            attach_opencode_task(command, binary, environment, workspace, job, prompt)
        write_handoff(job, "" if harness == "opencode" else prompt)
        output = run_child(command, environment, workspace, job, options.timeout)
        text = result_text(harness, output)
    return result | {"status": "completed", "text": redact(text)}


def harness_status(harness):
    try:
        environment = child_environment(harness)
        binary = executable(harness, environment)
        if harness == "claude":
            check_claude_settings(Path.cwd())
        return {"executable": binary, "auth": "see per-route checks" if harness == "opencode"
                else authenticate(harness, binary, environment)}
    except DispatchError as error:
        return {"error": str(error)}


def opencode_route_status(name, route, status, cache):
    try:
        if "executable" not in status:
            raise DispatchError("OpenCode executable is unavailable.")
        environment = child_environment("opencode")
        key = (route.get("model"), route.get("credential_id"), route.get("subscription_confirmed"))
        if key not in cache:
            cache[key] = authenticate_opencode(status["executable"], environment, route)
        verify_opencode_persona(status["executable"], environment, Path.cwd(), name)
        return {"auth": cache[key], "persona": "primary execution verified", "read_only": "disabled"}
    except DispatchError as error:
        return {"error": str(error), "read_only": "disabled"}


def doctor(agents):
    statuses = {harness: harness_status(harness) for harness in sorted({route["harness"] for route in agents.values()})}
    cache = {}
    route_checks = {name: opencode_route_status(name, route, statuses["opencode"], cache)
                    for name, route in agents.items() if route["harness"] == "opencode"}
    ready = not any("error" in status for status in (*statuses.values(), *route_checks.values()))
    missing = [name for name, route in agents.items() if not persona_path(name, route["harness"]).is_file()]
    return {"status": "ready" if ready and not missing else "needs-attention", "harnesses": statuses,
            "opencode_routes": route_checks, "missing_personas": missing, "live_model_access": "not checked"}


def terminated(signum, frame):
    raise DispatchError("Delegation terminated; native process cleanup requested.", 128 + signum)


def main():
    signal.signal(signal.SIGTERM, terminated)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(os.environ.get(
        "WORKFORCE_ROUTING_CONFIG", str(ROOT / "config" / "agent-routing.toml"))))
    commands = parser.add_subparsers(dest="operation", required=True)
    commands.add_parser("list", help="Show specialist routing without model calls")
    commands.add_parser("doctor", help="Check executables, native logins and deployed personas")
    task = commands.add_parser("delegate", help="Run one specialist task through its mapped CLI")
    task.add_argument("agent")
    task.add_argument("--task-file", type=Path)
    task.add_argument("--workspace", type=Path, default=Path.cwd())
    task.add_argument("--dry-run", action="store_true")
    task.add_argument("--allow-write", action="store_true")
    task.add_argument("--timeout", type=float, default=300)
    options = parser.parse_args()
    try:
        agents = routing(options.config.expanduser())
        if options.operation == "list":
            result = {"agents": agents}
        elif options.operation == "doctor":
            result = doctor(agents)
        else:
            if not 0 < options.timeout <= 3600:
                raise DispatchError("Timeout must be greater than zero and at most 3600 seconds.")
            result = delegate(options, agents)
        print(json.dumps(result, ensure_ascii=False))
        return 1 if result.get("status") == "needs-attention" else 0
    except DispatchError as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        return error.code
    except (OSError, UnicodeError, subprocess.TimeoutExpired):
        print(json.dumps({"status": "failed", "error": "Local prerequisite or filesystem operation failed; check paths and permissions."}))
        return 1
    except KeyboardInterrupt:
        print(json.dumps({"status": "failed", "error": "Delegation cancelled."}))
        return 130


if __name__ == "__main__":
    sys.exit(main())
