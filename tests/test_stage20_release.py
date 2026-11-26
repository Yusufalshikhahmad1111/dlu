from pathlib import Path

from dlu_app import __version__


ROOT = Path(__file__).parents[1]


def test_stage20_release_version_is_2_0_0():
    assert __version__ == "2.0.0"
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "2.0.0"' in pyproject


def test_stage20_release_workflow_and_qa_runner_exist():
    assert (ROOT / ".github" / "workflows" / "stage20-release.yml").exists()
    assert (ROOT / "tools" / "stage20_release_qa.py").exists()


def test_stage20_documentation_set_is_complete():
    required = (
        "docs/94-STAGE-20-PLAN.md",
        "docs/95-STAGE-20-IMPLEMENTATION-REPORT.md",
        "docs/96-STAGE-20-WINDOWS-QA.md",
        "docs/97-STAGE-20-ACADEMIC-GUIDE.md",
        "docs/98-STAGE-20-INSTRUCTOR-GUIDE.md",
        "docs/99-STAGE-20-CLOSEOUT.md",
    )
    for relative in required:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.read_text(encoding="utf-8").strip()


def test_stage20_release_documentation_is_synchronized():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    manual = (ROOT / "docs/32-USER-MANUAL.md").read_text(encoding="utf-8")
    milestones = (ROOT / "docs/05-MILESTONES.md").read_text(encoding="utf-8")
    assert "2.0.0" in readme
    assert "2.0.0" in manual
    assert "Stage 20" in milestones
