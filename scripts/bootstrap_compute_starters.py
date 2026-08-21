"""Create missing local-first Compute Lab starters without touching player edits."""

from pathlib import Path

COMPUTE_NODE_IDS = (
    'ne_comp1', 'ne_comp2', 'ne_comp3', 'ne_comp4', 'e_types', 'e_op_add',
    'e_op_sub', 'e_op_mul', 'e_op_div', 'e_op_mod', 'e_calc', 'se_comp1',
    's_comp1', 'sw_comp1', 'nw_comp1', 'nw_comp2', 'nw_locked1', 'l1_e_comp1',
    'l1_e_comp2', 'l1_nn_comp1', 'l1_s_comp1', 'l1_w_comp2',
)
STARTER_SOURCE = 'class ProblemSolver:\n    pass\n'


def relative_path(node_id: str) -> Path:
    """The public node identity is the whole deterministic filename contract."""
    if node_id not in COMPUTE_NODE_IDS:
        raise ValueError(f'Unknown compute node: {node_id}')
    return Path('problems') / f'{node_id}.py'


def ensure_compute_starters(root: Path) -> list[Path]:
    created = []
    for node_id in COMPUTE_NODE_IDS:
        destination = root / relative_path(node_id)
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(STARTER_SOURCE, encoding='utf-8')
        created.append(destination)
    return created


if __name__ == '__main__':
    created = ensure_compute_starters(Path(__file__).resolve().parents[1])
    print(f'Compute Lab starters ready ({len(created)} created; existing files preserved).')
