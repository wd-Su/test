def progress_percent(completed: int, goal: int) -> int:
    """Return the reading progress as a whole percentage, rounded down."""
    if goal <= 0:
        raise ValueError("Reading goal must be positive")
    if not 0 <= completed <= goal:
        raise ValueError("Completed books must be between zero and the goal")
    return completed * 100 // (goal)
