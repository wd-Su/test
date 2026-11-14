import json
from html import escape
from pathlib import Path

from reading import progress_percent

ROOT = Path(__file__).resolve().parent


def main() -> None:
    data = json.loads((ROOT / "reading.json").read_text(encoding="utf-8"))
    template = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    page = template.format(
        title=escape(data["title"]),
        completed=data["completed"],
        goal=data["goal"],
        percent=progress_percent(data["completed"], data["goal"]),
        note=escape(data["note"]),
    )

    output = ROOT / "dist" / "index.html"
    output.parent.mkdir(exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print("Built dist/index.html")


if __name__ == "__main__":
    main()
