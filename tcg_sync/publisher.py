
import os
import subprocess

class Publisher:
    """Commit + push al repo de GitHub.

    Si hay `github_token` (ej. en GitHub Actions, via secrets.GITHUB_TOKEN)
    lo usa para armar el remote con credenciales embebidas. Si no hay token
    (uso local normal), deja el remote `origin` tal cual esta y confia en
    las credenciales de git/gh ya configuradas en la maquina.
    """

    def __init__(self, repo_dir: str, github_repo: str, github_token: str | None = None):
        self.repo_dir = repo_dir
        self.token = github_token
        self.repo = github_repo  # ej: "usuario/mi-repo"

    def _run(self, *args, check=True):
        return subprocess.run(args, cwd=self.repo_dir, check=check,
                              capture_output=True, text=True)

    def publish(self, message: str = "chore: sync card data"):
        self._run("git", "config", "user.name", "tcg-sync-bot", check=False)
        self._run("git", "config", "user.email", "bot@tcg-sync.local", check=False)
        if self.token:
            remote = (f"https://x-access-token:{self.token}"
                      f"@github.com/{self.repo}.git")
            self._run("git", "remote", "remove", "origin", check=False)
            self._run("git", "remote", "add", "origin", remote)
        fetch = self._run("git", "fetch", "origin", "main", check=False)
        if fetch.returncode == 0:
            self._run("git", "reset", "--soft", "origin/main")
        self._run("git", "add", "data/")
        # Si no hay cambios, no commiteamos
        result = subprocess.run(["git", "status", "--porcelain", "data/"],
                                cwd=self.repo_dir, capture_output=True, text=True)
        if not result.stdout.strip():
            print("Sin cambios, nada que publicar.")
            return
        self._run("git", "commit", "-m", message)
        self._run("git", "push", "origin", "HEAD:main")
        print("✅ Push completo.")
