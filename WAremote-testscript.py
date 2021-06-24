from map2loop.project import Project
import time
t0 = time.time()
proj = Project(
    loopdata_state="WA"
)

bbox = {
    "minx": 515687.31005864, # region of interest for GMD paper
    "miny": 7473446.76593407,
    "maxx": 562666.860106543,
    "maxy": 7521273.57407786,
    "base": -3200,
    "top": 1200,
}
proj.update_config(
    out_dir='./gmd-model',
    overwrite='in-place',
    bbox_3d=bbox,
    proj_crs={'init': 'EPSG:28350'},
    quiet='all'
)
proj.config.c_l['intrusive']='banana'


proj.run()
t2 = time.time()
print("m2l",(t2-t0)/60.0,"minutes")