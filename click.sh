# Click-measure the two newest scans in Downloads (see backend/tests/pipeline/photos/README.md).
uv run --with opencv-python --with numpy "$(dirname "$0")/scripts/click_measure.py" --latest "$@"
