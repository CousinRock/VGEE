import ee
import geemap
import os
import torch

def init_earth_engine():
    """Initial Earth Engine"""
    project = os.environ.get("PROJECT")
    print('CUDA available', torch.cuda.is_available())
    print("CUDA version:", torch.version.cuda)
    if project:
        print(f"Project: {project}")
        # geemap.set_proxy(port=20171)
        ee.Authenticate()
        ee.Initialize(project=project)
    else:
        print("PROJECT environment variable is not set")