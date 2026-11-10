"""Exercise evaluation through the public CLI without Ollama."""

import re
from pathlib import Path

from typer.testing import CliRunner

from deskrag.cli import app
from deskrag.core.runio import read_json, read_jsonl
from deskrag.core.schemas import CaseResult, RunMeta, RunSummary

REPO = Path(__file__).resolve().parents[2]
ANSI_CODE = re.compile(r"\x1b\[[0-9;]*m")


def test_cli_writes_complete_run_and_resumes(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO)
    target = tmp_path / "cli-run"
    args = [
        "eval",
        "run",
        "--config",
        "configs/fake.yaml",
        "--cases",
        "data/samples/cases.jsonl",
        "--run-dir",
        str(target),
    ]
    cli = CliRunner()
    result = cli.invoke(app, args)
    assert result.exit_code == 0, result.output
    meta = read_json(target / "meta.json", RunMeta)
    summary = read_json(target / "summary.json", RunSummary)
    assert meta.dataset.split == "dev"
    assert meta.dataset.n_cases == 7
    assert summary.metrics["e2e_pass"] == 4 / 7
    assert summary.by_case_type
    assert len(read_jsonl(target / "results.jsonl", CaseResult)) == 7
    before = (target / "results.jsonl").read_bytes()
    resumed = cli.invoke(app, args + ["--resume"])
    assert resumed.exit_code == 0, resumed.output
    assert (target / "results.jsonl").read_bytes() == before


def test_cli_rejects_resume_without_directory():
    result = CliRunner().invoke(app, ["eval", "run", "--resume"])
    assert result.exit_code == 2
    # On GitHub Actions, Typer colors usage errors, with codes even inside "--run-dir".
    assert "requires --run-dir" in ANSI_CODE.sub("", result.output)


RETRIEVAL_ONLY_CONFIG = """\
name: retrieval-only-test
system: rag
corpus_dir: data/samples/corpus
retrieval:
  method: fake
  k: 3
llm:
  model: never-called
"""


def test_cli_retrieval_only_runs_without_ollama(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO)
    # Nothing listens on port 9, so any call to Ollama would fail this test.
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:9")
    config = tmp_path / "config.yaml"
    config.write_text(RETRIEVAL_ONLY_CONFIG, encoding="utf-8")
    target = tmp_path / "run"

    result = CliRunner().invoke(
        app,
        [
            "eval",
            "run",
            "--config",
            str(config),
            "--cases",
            "data/samples/cases.jsonl",
            "--retrieval-only",
            "--run-dir",
            str(target),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "hit@5: 1.0" in result.output
    meta = read_json(target / "meta.json", RunMeta)
    summary = read_json(target / "summary.json", RunSummary)
    assert meta.config["retrieval_only"] is True
    assert meta.dataset.n_cases == 7
    assert summary.metrics["hit@5"] == 1.0
    assert summary.metrics["e2e_pass"] is None
    assert len(read_jsonl(target / "results.jsonl", CaseResult)) == 7


def test_cli_retrieval_only_needs_a_rag_config(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO)
    result = CliRunner().invoke(
        app,
        [
            "eval",
            "run",
            "--config",
            "configs/fake.yaml",
            "--cases",
            "data/samples/cases.jsonl",
            "--retrieval-only",
            "--run-dir",
            str(tmp_path / "run"),
        ],
    )
    assert result.exit_code == 2
    # Typer may wrap the message, so check the option name, which is one unbroken word.
    assert "retrieval-only" in ANSI_CODE.sub("", result.output)


def test_cli_runs_only_the_listed_cases(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO)
    ids = tmp_path / "ids.txt"
    ids.write_text("# two sample cases\ns02\ns01\n", encoding="utf-8")
    target = tmp_path / "run"

    result = CliRunner().invoke(
        app,
        [
            "eval",
            "run",
            "--config",
            "configs/fake.yaml",
            "--cases",
            "data/samples/cases.jsonl",
            "--case-ids",
            str(ids),
            "--run-dir",
            str(target),
        ],
    )

    assert result.exit_code == 0, result.output
    meta = read_json(target / "meta.json", RunMeta)
    rows = read_jsonl(target / "results.jsonl", CaseResult)
    assert [row.case_id for row in rows] == ["s01", "s02"]
    assert meta.dataset.n_cases == 2
    assert str(ids) in meta.dataset.path


def test_cli_rejects_a_listed_case_outside_the_split(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO)
    ids = tmp_path / "ids.txt"
    ids.write_text("s01\ns04\n", encoding="utf-8")  # s04 is a test-split case

    result = CliRunner().invoke(
        app,
        [
            "eval",
            "run",
            "--config",
            "configs/fake.yaml",
            "--cases",
            "data/samples/cases.jsonl",
            "--case-ids",
            str(ids),
            "--run-dir",
            str(tmp_path / "run"),
        ],
    )

    assert result.exit_code == 2
    assert "s04" in ANSI_CODE.sub("", result.output)
