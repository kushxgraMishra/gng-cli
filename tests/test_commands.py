from typer.testing import CliRunner

from gng.cli import app
from gng.commands import doctor

runner = CliRunner()

# Built from pieces so this test file does not list itself as a note.
TAG = "TO" + "DO"
FIX = "FIX" + "ME"


# --- new ---------------------------------------------------------------------
def test_new_creates_a_project(tmp_path):
    result = runner.invoke(app, ["new", "hello-app", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    root = tmp_path / "hello-app"
    for relative in ["pyproject.toml", "README.md", ".gitignore",
                     "src/hello_app/__init__.py", "src/hello_app/cli.py",
                     "tests/test_cli.py"]:
        assert (root / relative).is_file(), relative


def test_new_refuses_to_overwrite(tmp_path):
    (tmp_path / "taken").mkdir()
    result = runner.invoke(app, ["new", "taken", "--dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_new_rejects_bad_names(tmp_path):
    for bad in ["1abc", "has space", "class"]:
        result = runner.invoke(app, ["new", bad, "--dir", str(tmp_path)])
        assert result.exit_code == 1, bad
        assert not any(tmp_path.iterdir()), bad


# --- doctor ------------------------------------------------------------------
def test_doctor_runs_and_names_python():
    result = runner.invoke(app, ["doctor"])
    assert "python" in result.output
    assert result.exit_code in (0, 1)


def test_doctor_flags_a_wrong_columns_variable(monkeypatch):
    monkeypatch.setenv("COLUMNS", "40")
    monkeypatch.setattr(doctor, "real_width", lambda: 72)
    kind, text, fix = doctor.terminal_check()
    assert kind == "warn"
    assert "40" in text and "72" in text
    assert fix


def test_doctor_accepts_a_matching_columns_variable(monkeypatch):
    monkeypatch.setenv("COLUMNS", "72")
    monkeypatch.setattr(doctor, "real_width", lambda: 72)
    assert doctor.terminal_check()[0] == "ok"


# --- todo --------------------------------------------------------------------
def test_todo_finds_notes(tmp_path):
    (tmp_path / "a.py").write_text(f"x = 1  # {TAG}: fix me\ny = 2\n")
    (tmp_path / "b.py").write_text(f"# {FIX} later\n")
    result = runner.invoke(app, ["todo", str(tmp_path)])
    assert result.exit_code == 0
    assert "a.py:1" in result.output and TAG in result.output
    assert "b.py:1" in result.output and FIX in result.output
    assert "2 notes in 2 files" in result.output


def test_todo_ignores_plain_words_and_skipped_folders(tmp_path):
    (tmp_path / "a.py").write_text(f'print("{TAG} is just a word here")\n')
    hidden = tmp_path / ".venv"
    hidden.mkdir()
    (hidden / "lib.py").write_text(f"# {TAG} hidden\n")
    result = runner.invoke(app, ["todo", str(tmp_path)])
    assert "no notes found" in result.output


def test_todo_reports_a_missing_path(tmp_path):
    result = runner.invoke(app, ["todo", str(tmp_path / "nope")])
    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_todo_shows_short_paths_inside_the_current_folder(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text(f"# {TAG} x\n")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["todo", "."])
    assert "\n  a.py:1" in result.output


def test_todo_shows_absolute_paths_outside_the_current_folder(tmp_path, monkeypatch):
    work = tmp_path / "work"
    other = tmp_path / "other"
    work.mkdir()
    other.mkdir()
    (other / "a.py").write_text(f"# {TAG} x\n")
    monkeypatch.chdir(work)
    result = runner.invoke(app, ["todo", str(other)])
    assert str(other / "a.py") in result.output
    assert "../" not in result.output


# --- clean -------------------------------------------------------------------
def test_clean_dry_run_deletes_nothing(tmp_path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "x.pyc").write_bytes(b"abc")
    result = runner.invoke(app, ["clean", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert cache.exists()


def test_clean_yes_removes_only_caches(tmp_path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("print(1)\n")
    venv_cache = tmp_path / ".venv" / "__pycache__"
    venv_cache.mkdir(parents=True)
    result = runner.invoke(app, ["clean", str(tmp_path), "--yes"])
    assert result.exit_code == 0
    assert not cache.exists()
    assert (src / "main.py").exists()
    assert venv_cache.exists()  # .venv is never touched


def test_clean_will_not_delete_without_a_terminal_or_yes(tmp_path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    result = runner.invoke(app, ["clean", str(tmp_path)])
    assert result.exit_code == 1
    assert cache.exists()
    assert "--yes" in result.output
