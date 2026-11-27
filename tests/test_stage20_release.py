from pathlib import Path

from dlu_app import APP_NAME, __version__


ROOT = Path(__file__).parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_stage20_release_identity_is_2_0_0():
    assert APP_NAME == "DLU Lab"
    assert __version__ == "2.0.0"
    assert 'version = "2.0.0"' in _read("pyproject.toml")


def test_stage20_release_documents_are_present_and_synchronised():
    required = (
        "docs/94-DLU-LAB-2.0-ACADEMIC-GUIDE.md",
        "docs/95-DLU-LAB-2.0-INSTRUCTOR-GUIDE.md",
        "docs/96-STAGE-20-PLAN.md",
        "docs/97-STAGE-20-IMPLEMENTATION-REPORT.md",
        "docs/98-STAGE-20-WINDOWS-QA.md",
        "docs/99-STAGE-20-CLOSEOUT.md",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    manual = _read("docs/32-USER-MANUAL.md")
    academic = _read("docs/94-DLU-LAB-2.0-ACADEMIC-GUIDE.md")
    instructor = _read("docs/95-DLU-LAB-2.0-INSTRUCTOR-GUIDE.md")

    assert "DLU Lab 2.0.0" in manual
    assert "Stage 20" in manual
    assert "DLU Lab 2.0.0" in academic
    assert "DLU Lab 2.0.0" in instructor


def test_stage20_release_workflow_has_full_release_gates():
    workflow = _read(".github/workflows/stage20-release.yml")
    for marker in (
        "Full regression",
        "Stage 17 accessibility compatibility",
        "Stage 18 architecture compatibility",
        "Stage 19 academic compatibility",
        "Stage 20 focused release checks",
        "Windows Stage 20 visual QA",
        "Build and smoke-test Windows release",
        "DLU_RELEASE_PROBE",
        "DLU_VERSION_FILE",
        "DLU-Lab-2.0.0-Windows",
    ):
        assert marker in workflow


def test_stage20_release_qa_covers_target_resolutions_and_the_academic_journey():
    qa = _read("tools/stage20_release_qa.py")
    for marker in (
        "(1280, 720)",
        "(1366, 768)",
        "(1600, 900)",
        "(1920, 1080)",
        'navigate_student_area("OMT / MML")',
        "quick_local()",
        "run_current()",
        "teaching_scenarios.run_selected()",
        "instructor_mode.run_selected()",
        "reveal_toggle",
        "set_projector_mode(True)",
    ):
        assert marker in qa


def test_stage20_packaging_still_uses_pyside6_onefile_deployment():
    pyproject = _read("pyproject.toml")
    build = _read("tools/build_windows.ps1")
    assert "[tool.pyside6.deploy]" in pyproject
    assert 'mode = "onefile"' in pyproject
    assert "pyside6-deploy --force --no-warn --mode onefile main.py" in build
