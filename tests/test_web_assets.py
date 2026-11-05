from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_web_studio_assets_exist():
    assert (ROOT/"web/index.html").is_file()
    assert (ROOT/"web/app.js").is_file()
    assert (ROOT/"web/styles.css").is_file()
def test_renderer_has_required_sandbox_flags():
    source=(ROOT/"drawing_engine/render_frames.js").read_text()
    assert "--no-sandbox" in source
    assert "--disable-setuid-sandbox" in source
