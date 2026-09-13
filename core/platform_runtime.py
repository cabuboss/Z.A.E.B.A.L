"""Small stdlib-only OS boundary; the audit protocol is shared."""

import base64
import contextlib
import os
import shlex
import time

if os.name == "nt":
    import msvcrt
else:
    import fcntl


def shell_command(argv):
    """Render for the native host shell, without interpreting path contents.

    Windows uses an explicit PowerShell launcher so the outer host may use
    either cmd or PowerShell. The encoded script contains only fixed argv;
    the user's hook payload continues to arrive on stdin.
    """
    if os.name != "nt":
        return shlex.join([str(arg) for arg in argv])
    quoted = " ".join("'" + str(arg).replace("'", "''") + "'" for arg in argv)
    script = "& " + quoted + "; exit $LASTEXITCODE"
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    return "powershell.exe -NoProfile -NonInteractive -EncodedCommand " + encoded


@contextlib.contextmanager
def state_lock(path, timeout=5):
    """Lock a stable file across read/modify/replace, on both supported OSes.

    A timeout raises to the hook's fail-open boundary; never update shared
    state without the lock. OS releases the lock if the process terminates.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+b") as handle:
        if os.name == "nt":
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                if os.name == "nt":
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("state lock unavailable")
                time.sleep(0.02)
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def sync_directory(path):
    # Windows cannot open directories through os.open for POSIX fsync.
    # File data is flushed before os.replace on both platforms.
    if os.name != "nt":
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
