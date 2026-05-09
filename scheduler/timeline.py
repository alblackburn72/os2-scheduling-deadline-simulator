from scheduler.models import ExecutionSegment


def add_exec_segment(
    execution_segments: list[ExecutionSegment],
    pid: str,
    start_time: int,
    end_time: int,
) -> None:
    """
    Dodaje novi execution segment u vremensku liniju

    Ako prethodni segment pripada istom procesu i zavrsava se tacno kad nov
    pocne, dva segmenta se spajaju
    """

    if start_time == end_time:
        return

    if (
        execution_segments
        and execution_segments[-1].pid == pid
        and execution_segments[-1].end_time == start_time
    ):

        previous_segment = execution_segments[-1]

        execution_segments[-1] = ExecutionSegment(
            pid=pid,
            start_time=previous_segment.start_time,
            end_time=end_time,
        )

        return

    execution_segments.append(
        ExecutionSegment(pid=pid, start_time=start_time, end_time=end_time)
    )
