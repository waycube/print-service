import os


def get_templates():
    """
    Returns templates relative to templates/grocy/
    Output format:
        ["grocy/template1.glabels", ...]
    """

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../")
    )

    TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates", "grocy")

    if not os.path.exists(TEMPLATE_DIR):
        return []

    templates = []

    for file in os.listdir(TEMPLATE_DIR):
        if file.endswith(".glabels"):
            templates.append(f"grocy/{file}")

    return templates