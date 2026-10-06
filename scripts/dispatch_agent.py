#!/usr/bin/env python3
"""Delegate local specialist tasks through authenticated native CLIs."""

import argparse
import fcntl
import json
import os
import re
import shutil
import signal
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


class DispatchError(Exception):
    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def routing(path):
    try:
        config = tomllib.loads(path.read_text())
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise DispatchError("Cannot read routing TOML; check --config.") from error
    agents = config.get("agents")
    if type(config.get("version")) is not int or config.get("version") != 1 or not isinstance(agents, dict) or not agents:
        raise DispatchError("Routing requires version = 1 and a non-empty agents table.")
    for name, route in agents.items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name) or not isinstance(route, dict):
            raise DispatchError("Routing contains an invalid specialist definition.")
        if route.get("harness") not in ("codex", "claude", "opencode"):
            raise DispatchError("Routing harness must be codex, claude or opencode.")
        model = route.get("model", "")
        if not isinstance(model, str) or (model and not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_./:#-]*", model)):
            raise DispatchError("Routing model must be a native model identifier, not command arguments.")
        if set(route) - {"harness", "model", "subscription_confirmed", "credential_id"}:
            raise DispatchError("Routing contains unsupported specialist settings.")
        if "subscription_confirmed" in route and type(route["subscription_confirmed"]) is not bool:
            raise DispatchError("Subscription confirmation must be a boolean.")
        if "credential_id" in route and (not isinstance(route["credential_id"], str)
                                         or not re.fullmatch(r"[a-zA-Z0-9_-]+", route["credential_id"])):
            raise DispatchError("Credential ID must be native non-secret metadata, not a credential value.")
        if route["harness"] != "opencode" and set(route) & {"subscription_confirmed", "credential_id"}:
            raise DispatchError("Subscription attestation fields apply only to OpenCode routes.")
    return agents


def child_environment(harness):
    environment = dict(os.environ)
    for variable in API_OVERRIDES.get(harness, ()):
        environment.pop(variable, None)
    if harness == "claude":
        environment.pop("CLAUDECODE", None)
    return environment


def executable(harness, environment):
    candidate = environment.get("WORKFORCE_" + harness.upper(), harness)
    found = shutil.which(candidate, path=environment.get("PATH", ""))
    if not found:
        raise DispatchError(f"{harness} executable not found; configure WORKFORCE_{harness.upper()} or PATH.")
    return found


def metadata_command(command, environment, workspace=None):
    with tempfile.TemporaryDirectory(prefix="workforce-metadata-") as directory:
        job = Path(directory)
        output, final = run_child(command, environment, workspace, job, "", 15)
        errors = (job / "stderr.txt").read_text(errors="replace")
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
    for integration in integrations:
        if not isinstance(integration, dict) or integration.get("id") != provider:
            continue
        connections = integration.get("connections")
        if isinstance(connections, list) and connections and isinstance(connections[0], dict):
            active = connections[0]
            if (active.get("type") == "credential" and active.get("id") == route["credential_id"]
                    and active.get("method") in ("key", "oauth")):
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
        directory = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    else:
        directory = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "opencode"
    return directory / "agents" / (name + ".md")


def check_claude_settings(workspace):
    directory = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    paths = [directory / "settings.json", directory / "settings.local.json",
             workspace / ".claude" / "settings.json", workspace / ".claude" / "settings.local.json",
             Path("/Library/Application Support/ClaudeCode/managed-settings.json")]
    for path in paths:
        if not path.is_file():
            continue
        try:
            settings = json.loads(path.read_text())
        except (OSError, UnicodeError, ValueError) as error:
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


def command_for(binary, name, route, write, result_file):
    harness = route["harness"]
    if harness == "codex":
        command = [binary, "exec", "--sandbox", "workspace-write" if write else "read-only",
                   "--json", "--color", "never", "--output-last-message", str(result_file),
                   "-c", 'forced_login_method="chatgpt"', "-c", 'model_provider="openai"']
    elif harness == "claude":
        command = [binary, "--print", "--agent", name, "--output-format", "json",
                   "--permission-mode", "manual" if write else "plan",
                   "--disallowedTools", "Agent,Task", "--settings",
                   json.dumps({"env": {variable: "" for variable in API_OVERRIDES["claude"]},
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
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise DispatchError("Another workforce task is running in this workspace; retry after it completes.") from error
        with tempfile.TemporaryDirectory(prefix="job-", dir=runtime) as directory:
            yield Path(directory)
    finally:
        os.close(descriptor)


def stop_process(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def run_child(command, environment, workspace, job, prompt, timeout):
    input_file = job / "input.txt"
    input_file.write_text(prompt)
    input_file.chmod(0o600)
    stdout_file, stderr_file = job / "stdout.jsonl", job / "stderr.txt"
    result_file = job / "result.txt"
    for path in (stdout_file, stderr_file, result_file):
        path.touch(mode=0o600)
    with input_file.open("rb") as source, stdout_file.open("wb") as output, stderr_file.open("wb") as errors:
        process = subprocess.Popen(command, env=environment, cwd=workspace, stdin=source,
                                   stdout=output, stderr=errors, start_new_session=True)
        deadline = time.monotonic() + timeout
        try:
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    raise DispatchError("Native CLI task timed out; its process group was stopped.", 124)
                if sum(path.stat().st_size for path in (stdout_file, stderr_file, result_file)) > MAX_OUTPUT:
                    raise DispatchError("Native CLI output exceeded the safety limit; its process group was stopped.")
                time.sleep(0.05)
        finally:
            stop_process(process)
    if sum(path.stat().st_size for path in (stdout_file, stderr_file, result_file)) > MAX_OUTPUT:
        raise DispatchError("Native CLI output exceeded the safety limit.")
    if process.returncode:
        raise DispatchError(f"Native CLI exited with status {process.returncode}; check its login, model and permissions.")
    return stdout_file.read_text(errors="replace"), result_file.read_text(errors="replace")


def result_text(harness, output, final):
    text = []
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
        if harness == "claude" and event.get("type") == "result" and isinstance(event.get("result"), str):
            text.append(event["result"])
        if harness == "opencode" and event.get("type") == "text":
            part = event.get("part", {})
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                text.append(part["text"])
    result = final.strip() if harness == "codex" else "\n".join(text).strip()
    if not result:
        raise DispatchError("Native CLI returned no final specialist response; no success is assumed.")
    return result


def redact(text):
    for name, value in os.environ.items():
        if len(value) >= 8 and re.search(r"TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY", name, re.I):
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"-----BEGIN [^-\n]*PRIVATE KEY-----.*?-----END [^-\n]*PRIVATE KEY-----",
                  "[REDACTED PRIVATE KEY]", text, flags=re.S)
    text = re.sub(r"\bBearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", text, flags=re.I)
    text = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{20,})", "[REDACTED]", text)
    return text


def delegate(options, agents):
    if options.agent not in agents:
        raise DispatchError("Unknown specialist; run workforce list.")
    if options.allow_write and options.agent in ADVISORY:
        raise DispatchError("Architecture guardian and principal engineer are advisory; write access is refused.")
    workspace = options.workspace.expanduser().resolve()
    if not workspace.is_dir():
        raise DispatchError("Workspace must be an existing directory.")
    if options.task_file:
        path = options.task_file.expanduser()
        if path.stat().st_size > MAX_TASK:
            raise DispatchError("Task file exceeds the safety limit.")
        task = path.read_text()
    else:
        if sys.stdin.isatty():
            raise DispatchError("Provide --task-file or pipe a task on stdin.")
        task = sys.stdin.read(MAX_TASK + 1)
    if not task.strip() or len(task.encode()) > MAX_TASK:
        raise DispatchError("Task must be non-empty and at most 64 KiB.")
    route = agents[options.agent]
    harness = route["harness"]
    result = {"agent": options.agent, "harness": harness, "model": route.get("model") or "configured-default",
              "workspace": str(workspace), "access": "workspace-write" if options.allow_write else "read-only"}
    if options.dry_run:
        blocked = harness == "opencode" and (not options.allow_write or not route.get("subscription_confirmed")
                  or not route.get("credential_id") or "/" not in route.get("model", ""))
        return result | {"status": "dry-run", "blocked": blocked, "prerequisites": "not checked",
                         "command": command_for(harness, options.agent, route,
                                                options.allow_write, "<private-result-file>")}
    if harness == "opencode" and not options.allow_write:
        raise DispatchError("OpenCode read-only delegation is disabled: effective native restrictions are not verified. Use a read-only Codex/Claude route for reviews; do not grant writes to bypass this guard.")
    if os.environ.get("WORKFORCE_ACTIVE"):
        raise DispatchError("Recursive workforce delegation is refused; return control to the coordinator.")
    persona = require_persona(options.agent, harness)
    environment = child_environment(harness)
    binary = executable(harness, environment)
    if harness == "claude":
        check_claude_settings(workspace)
    authenticate(harness, binary, environment, route, workspace)
    if harness == "opencode":
        verify_opencode_persona(binary, environment, workspace, options.agent)
    environment["WORKFORCE_ACTIVE"] = "1"
    if not shutil.which("git", path=environment.get("PATH", "")):
        raise DispatchError("Git is required to validate the workspace.")
    checked = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=workspace,
                             capture_output=True, text=True, timeout=10)
    if checked.returncode:
        raise DispatchError("Delegation requires a Git workspace.")
    worktree = Path(checked.stdout.strip()).resolve()
    if harness == "claude" and worktree != workspace:
        check_claude_settings(worktree)
    prompt = (f"You are handling a delegated {options.agent} task. Complete only this task and return your findings. "
              "Do not recursively delegate through workforce. Do not commit, push or deploy. "
              "Never include secrets, tokens, private keys or sensitive payloads in your response.\n\n")
    if persona:
        prompt += "Specialist operating instructions:\n" + persona + "\n\n"
    prompt += "Coordinator task:\n" + task
    with workspace_job(worktree) as job:
        command = command_for(binary, options.agent, route, options.allow_write, job / "result.txt")
        if harness == "opencode":
            help_result = metadata_command([binary, "run", "--help"], environment, workspace)
            if help_result.returncode:
                raise DispatchError("Cannot inspect OpenCode run capabilities.")
            if "--standalone" in help_result.stdout:
                command.append("--standalone")
            prompt_file = job / "task.md"
            prompt_file.write_text(prompt)
            prompt_file.chmod(0o600)
            command += ["--file", str(prompt_file), "Complete the delegated task in the attached file."]
        output, final = run_child(command, environment, workspace, job,
                                  "" if harness == "opencode" else prompt, options.timeout)
        text = result_text(harness, output, final)
    return result | {"status": "completed", "text": redact(text)}


def doctor(agents):
    statuses, ready = {}, True
    for harness in sorted({route["harness"] for route in agents.values()}):
        try:
            environment = child_environment(harness)
            binary = executable(harness, environment)
            if harness == "claude":
                check_claude_settings(Path.cwd())
            statuses[harness] = {"executable": binary, "auth": "see per-route checks" if harness == "opencode"
                                 else authenticate(harness, binary, environment)}
        except DispatchError as error:
            ready = False
            statuses[harness] = {"error": str(error)}
    route_checks, cache = {}, {}
    for name, route in agents.items():
        if route["harness"] != "opencode":
            continue
        key = (route.get("model"), route.get("credential_id"), route.get("subscription_confirmed"))
        if key not in cache:
            try:
                if "executable" not in statuses["opencode"]:
                    raise DispatchError("OpenCode executable is unavailable.")
                cache[key] = {"auth": authenticate_opencode(statuses["opencode"]["executable"],
                                                          child_environment("opencode"), route)}
            except DispatchError as error:
                cache[key] = {"error": str(error)}
        route_checks[name] = cache[key] | {"read_only": "disabled"}
        if "error" in cache[key]:
            ready = False
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
