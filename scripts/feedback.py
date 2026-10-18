"""Run the existing bounded ThreadDesk feedback watcher with the pinned store."""
from host import SOURCE, Host
import runpy
import sys
import time
from pathlib import Path
if __name__=='__main__':
    h=Host()
    # The existing watcher scans without a delay. Throttle only this process's
    # bound board, preserving its 60-second timer and the unchanged host source.
    board = h.store.root/'whiteboard'/h.thread_id
    original_glob = Path.glob
    def polled_glob(path, pattern, *args, **kwargs):
        if path == board:
            time.sleep(.25)
        return original_glob(path, pattern, *args, **kwargs)
    Path.glob = polled_glob
    # Host has already imported the concurrency-safe pinned services.
    sys.argv[1:1]=['--root',str(h.store.root),'--thread',h.thread_id]
    runpy.run_path('/Users/landjunge/threaddesk/scripts/whiteboard_feedback_watch.py',run_name='__main__')
