import os
from typing import List


def get_templates() -> List[str]:
    """
    Returns list of available .glabels templates in app directory.
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = BASE_DIR  # templates liggen direct in app/

    templates = []

    for file in os.listdir(templates_dir):
        if file.endswith(".glabels"):
            templates.append(file)

    return templates