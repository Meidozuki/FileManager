from collections.abc import Sequence


def source_index_for_view_row(
    visible_source_indices: Sequence[int],
    view_row: int,
) -> int:
    """Resolve a table view row to its immutable source-list index."""
    if not isinstance(view_row, int):
        raise TypeError(f"view row must be int, got {type(view_row).__name__}")
    if view_row < 0 or view_row >= len(visible_source_indices):
        raise IndexError(f"view row out of range: {view_row}")

    source_index = visible_source_indices[view_row]
    if not isinstance(source_index, int) or source_index < 0:
        raise ValueError(f"invalid source index: {source_index}")
    return source_index
