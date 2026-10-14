from __future__ import annotations

from pathlib import Path
import pytest

from dailybrief.doctor import (
    DoctorCheck,
    check_cache_health,
    check_config,
    check_git,
    check_notes_dir,
    check_provider,
    check_voice_availability,
    render_doctor_table,
    run_doctor,
)


def test_check_config_missing(tmp_path: Path) -> None:
    non_existent = tmp_path / "missing_config.toml"
    chk = check_config(non_existent)
    assert chk.status == "WARN"
    assert "Not found" in chk.details


def test_check_config_valid(tmp_path: Path) -> None:
    valid_cfg = tmp_path / "config.toml"
    valid_cfg.write_text('provider = "anthropic"\nmodel = "claude-sonnet-4-6"\n', encoding="utf-8")
    chk = check_config(valid_cfg)
    assert chk.status == "PASS"
    assert "anthropic" in chk.details


def test_check_config_invalid(tmp_path: Path) -> None:
    broken_cfg = tmp_path / "broken.toml"
    broken_cfg.write_text('invalid = [unclosed', encoding="utf-8")
    chk = check_config(broken_cfg)
    assert chk.status == "FAIL"


def test_check_notes_dir(tmp_path: Path) -> None:
    # 1. Missing
    missing = tmp_path / "non_existent"
    assert check_notes_dir(missing).status == "WARN"

    # 2. Empty directory
    notes = tmp_path / "notes"
    notes.mkdir()
    assert check_notes_dir(notes).status == "WARN"

    # 3. With notes
    (notes / "a.md").write_text("note", encoding="utf-8")
    chk = check_notes_dir(notes)
    assert chk.status == "PASS"
    assert "1" in chk.details


def test_check_cache_health() -> None:
    chk = check_cache_health()
    assert chk.status == "PASS"


def test_check_voice_availability() -> None:
    chk = check_voice_availability()
    assert chk.status in ("PASS", "WARN")


def test_run_doctor_and_render_table(tmp_path: Path) -> None:
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "tasks.md").write_text("- Hello", encoding="utf-8")

    checks = run_doctor(lang="en", notes_dir=notes_dir)
    assert len(checks) >= 5
    assert all(isinstance(c, DoctorCheck) for c in checks)

    table = render_doctor_table(checks, lang="en")
    assert table.title == "DailyBrief System Diagnostics (Doctor)"
    assert len(table.rows) == len(checks)

    table_tr = render_doctor_table(checks, lang="tr")
    assert "Tanılama" in table_tr.title
