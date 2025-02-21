import ee
import geemap
import os

def init_earth_engine():
    """Initial Earth Engine"""
    project = os.environ.get("PROJECT")
    if project:
        print(f"Project: {project}")
        # geemap.set_proxy(port=port)
        ee.Authenticate()
        ee.Initialize(project=project)
    else:
        print("PROJECT environment variable is not set")