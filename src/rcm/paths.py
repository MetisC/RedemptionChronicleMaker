from pathlib import Path


class Workspace:
    """Every write resolves beneath the workspace and outside the game."""
    def __init__(self, root: Path, game: Path | None = None):
        self.root = root.resolve()
        self.game = game.resolve() if game else None
        if self.game and self.root.is_relative_to(self.game):
            raise ValueError("El workspace no puede estar dentro del juego original")

    def output(self, path: str | Path) -> Path:
        candidate = self.root / path
        for part in [candidate, *candidate.parents]:
            if part == self.root:
                break
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError(f"Salida a través de enlace: {part}")
            if part.is_file() and part.stat().st_nlink != 1:
                raise ValueError(f"Salida sobre hardlink: {part}")
        dest = candidate.resolve()
        if not dest.is_relative_to(self.root):
            raise ValueError(f"Salida fuera del workspace: {dest}")
        if self.game and dest.is_relative_to(self.game):
            raise ValueError("La instalación original es de solo lectura")
        for part in [dest, *dest.parents]:
            if part == self.root:
                break
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError(f"Salida a través de enlace: {part}")
        return dest

    def write(self, path: str | Path, data: bytes | str) -> Path:
        dest = self.output(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
        return dest
