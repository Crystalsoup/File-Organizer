from pathlib import Path
import file_organizer.__main__ as cli

def test_plan_ext(tmp_path: Path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "b.TXT").write_text("y")
    (tmp_path / "c").write_text("z")
    ops = cli.plan_moves(tmp_path, tmp_path, "ext")
    assert len(ops) == 3
    assert any(str(dst).endswith("no_ext/c") for _, dst in ops)
