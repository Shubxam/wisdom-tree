import os
import subprocess
import sys
from pathlib import Path


def test_importing_edit_quotes_has_no_file_side_effects(tmp_path: Path) -> None:
    project_root = Path(__file__).parents[1]
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root / 'src')

    result = subprocess.run(
        [sys.executable, '-c', 'import wisdom_tree.edit_quotes'],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not (tmp_path / 'edited_quotes.txt').exists()
