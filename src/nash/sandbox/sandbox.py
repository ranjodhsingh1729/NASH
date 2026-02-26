import uuid
import subprocess


class Sandbox:
    def __init__(self, image="ubuntu:24.04"):
        self.image = image
        self.container_id = None
        self.container_name = f"sandbox_{uuid.uuid4().hex[:8]}"
        self.init()

    def init(self):
        result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--rm",
                "--name",
                self.container_name,
                self.image,
                "sleep",
                "infinity",
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )

        self.container_id = result.stdout.strip()

        # Ensure bash exists (Ubuntu does, but defensive)
        self.exec_shell("apt-get update -y", check=False)
        return result

    def kill(self):
        if not self.container_id:
            return None

        return subprocess.run(
            ["docker", "kill", self.container_id],
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )

    def reset(self):
        self.kill()
        return self.init()

    def exec(self, args, **kwargs):
        cmd = ["docker", "exec", self.container_id] + args
        return subprocess.run(cmd, **kwargs)

    def exec_shell(self, command, timeout=30, check=False):
        """
        Execute a full shell command inside the container.
        Supports pipes, redirects, &&, etc.
        """
        return subprocess.run(
            [
                "docker",
                "exec",
                self.container_id,
                "bash",
                "-lc",
                command,
            ],
            text=True,
            capture_output=True,
            timeout=timeout,
            check=check,
        )

    def __del__(self):
        try:
            self.kill()
        except Exception:
            pass
