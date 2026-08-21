from pathlib import Path

from scripts.bootstrap_compute_starters import COMPUTE_NODE_IDS, STARTER_SOURCE, ensure_compute_starters, relative_path


def test_every_known_compute_node_has_a_canonical_empty_starter():
    root = Path(__file__).resolve().parents[1]
    assert len(COMPUTE_NODE_IDS) == len(set(COMPUTE_NODE_IDS))
    for node_id in COMPUTE_NODE_IDS:
        path = root / relative_path(node_id)
        assert path.read_text(encoding='utf-8') == STARTER_SOURCE


def test_bootstrap_creates_missing_starter_but_never_replaces_player_code(tmp_path):
    preserved = tmp_path / relative_path('e_op_add')
    preserved.parent.mkdir(parents=True)
    preserved.write_text('class ProblemSolver:\n    def solution(self): return 42\n', encoding='utf-8')

    created = ensure_compute_starters(tmp_path)

    assert len(created) == len(COMPUTE_NODE_IDS) - 1
    assert preserved.read_text(encoding='utf-8') == 'class ProblemSolver:\n    def solution(self): return 42\n'
    assert (tmp_path / relative_path('nw_locked1')).read_text(encoding='utf-8') == STARTER_SOURCE
