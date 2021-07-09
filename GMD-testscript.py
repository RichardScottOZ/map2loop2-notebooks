# Example test python script to accompany the GMD paper:
# Automated geological map deconstruction for 3D model construction using map2loop 1.0 and map2model 1.0 
# Mark Jessell, Vitaliy Ogarko, Yohan de Rose, Mark Lindsay, Ranee Joshi, Agnieszka Piechocka, Lachlan Grose, 
# Miguel de la Varga, Laurent Ailleres, Guillaume Pirot
# https://doi.org/10.5194/gmd-2020-400

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
proj_path = proj.config.project_path
graph_path = proj.config.graph_path
tmp_path = proj.config.tmp_path
data_path = proj.config.data_path
dtm_path = proj.config.dtm_path
output_path = proj.config.output_path
vtk_path = proj.config.vtk_path

# Define project bounds
minx,miny,maxx,maxy = proj.config.bbox
model_base = proj.config.bbox_3d['base']
model_top = proj.config.bbox_3d['top']

fault_file = proj.config.fault_file_csv

from LoopStructural import GeologicalModel
from LoopStructural.visualisation import LavaVuModelViewer
from datetime import datetime
import os
import time
from datetime import datetime
import shutil
import logging
logging.getLogger().setLevel(logging.ERROR)
import lavavu
import numpy as np  
import math
surface_verts = {}

    
def function(xyz,tri,name):
    xyz = np.copy(xyz)
    tri = np.copy(tri)
    nanmask = np.all(~np.isnan(xyz),axis=1)
    vert_idx = np.zeros(xyz.shape[0],dtype=int) -1
    vert_idx[nanmask] = np.arange(np.sum(nanmask))
    tri[:] = vert_idx[tri]
    tri = tri[np.all(tri > -1,axis=1),:]
    xyz = xyz[nanmask,:]
    surface_verts[name] = (xyz,tri)
    
t1 = time.time()
print("m2l",(t1-t0)/60.0)

nowtime=datetime.now().isoformat(timespec='minutes')   
model_name='leaflet'+'_'+nowtime.replace(":","-").replace("T","-")
if (os.path.exists(vtk_path+model_name)):
    shutil.rmtree(vtk_path+model_name)
os.mkdir(vtk_path+model_name)
filename=vtk_path+model_name+'/'+'surface_name_{}.vtk'


f=open(tmp_path+'/bbox.csv','w')
f.write('minx,miny,maxx,maxy,lower,upper\n')
ostr='{},{},{},{},{},{}\n'.format(minx,miny,maxx,maxy,model_base,model_top)
f.write(ostr)
f.close()


fault_params = {'interpolatortype':'FDI',
                'nelements':1e5,
                'step':10,
                'fault_buffer':0.3,
                'solver':'cg',
                'cpw':10,
                'npw':10}
foliation_params = {'interpolatortype':'FDI' , # 'interpolatortype':'PLI',
                    'nelements':1e5,  # how many tetras/voxels
                    'buffer':1.8,  # how much to extend nterpolation around box
                    'solver':'cg',
                    'cpw':10,
                    'npw':10}
model, m2l_data = GeologicalModel.from_map2loop_directory(proj_path,
                                                          #    evaluate=False,
                                                          fault_params=fault_params,
                                                          rescale=False,
                                                          foliation_params=foliation_params,
                                                         )
#model.to_file(output_path + "/model.pickle")    

view = LavaVuModelViewer(model,vertical_exaggeration=1) 
view.nsteps = np.array([200,200,200])
view.nsteps=np.array([50,50,50])

for sg in model.feature_name_index:
    if( 'super' in sg):
        view.add_data(model.features[model.feature_name_index[sg]])
view.nelements = 1e5
view.add_model_surfaces(function=function,filename=filename,faults=False)
view.nelements=1e6
view.add_model_surfaces(function=function,filename=filename,strati=False,displacement_cmap = 'rainbow')
view.lv.webgl(vtk_path+model_name)
view.nsteps = np.array([200,200,200])

view.add_model()

view.lv.control.Range('alpha', label="Global Opacity")
view.lv.control.DualRange(['xmin', 'xmax'], label="x clip", step=0.01, values=[0.0,1.0])
view.lv.control.DualRange(['ymin', 'ymax'], label="y clip", step=0.01, values=[0.0,1.0])
view.lv.control.DualRange(['zmin', 'zmax'], label="z clip", step=0.01, values=[0.0,1.0])
view.lv.control.Range(command='background', range=(0,1), step=0.1, value=0.8)
view.lv.control.show() #Show the control panel, including the viewer window


for layer in surface_verts:
    f=open(vtk_path+model_name+'/'+layer.replace("_iso_0.000000","")+'.obj','w')
    vert=surface_verts[layer][0].shape[0]
    tri=surface_verts[layer][1].shape[0]
    for v in range(0,vert):
        ostr = "v {} {} {}\n"\
            .format(surface_verts[layer][0][v][0],surface_verts[layer][0][v][1],surface_verts[layer][0][v][2])
        f.write(ostr)
    for t in range(0,tri):
        ostr = "f {} {} {}\n"\
                .format(surface_verts[layer][1][t][0]+1,surface_verts[layer][1][t][1]+1,surface_verts[layer][1][t][2]+1)
        f.write(ostr)
    first=False
    f.close()

t2 = time.time()
print("surfaces saved as vtk and obj formats in directory",vtk_path+model_name)
print("m2l",(t1-t0)/60.0,"LoopStructural",(t2-t1)/60.0,"Total",(t2-t0)/60.0,"minutes")
view.interactive()  
