from samgeo import SamGeo
from samgeo.text_sam import LangSAM

def segment_img(url):
    sam = LangSAM()
    text_prompt = "tree"
    sam.predict(url, text_prompt, box_threshold=0.24, text_threshold=0.24)
    return sam.result


