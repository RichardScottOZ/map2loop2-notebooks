# Example code snippets to support export of LoopStructural data in various triangulated surface and voxel formats
# Licensed under MIT license
# Mark Jessell 2021


# #code to take vertices info from your code and turn it into .obj files for Leapfrog 
#(note .obj meshes are 1 based) the first part of the code should be placed prior to LoopStructural model calculations, teh

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
#build model with LoopStructural then add this code to create vtk and obj surfaces
view.add_model_surfaces(function=function,filename=filename,faults=False)

for layer in surface_verts:
    vert=surface_verts[layer][0].shape[0]
    tri=surface_verts[layer][1].shape[0]
    
    if(len(vert)>0 and len(tri)>0):
        f=open(vtk_path+model_name+'/'+layer.replace("_iso_0.000000","")+'.obj','w')
        print(layer.replace("_iso_0.000000",""),vert,tri)
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


#code to parse a directory of .obj files and combine them into
#a single geoh5 file that GeoscienceAnalyst can read
#Requires installation of https://github.com/MiraGeoscience/geoh5py 
#(note .geoh5 meshes are 0 based)
#Run this code after obj files have been created (see above)

import pandas as pd
from os import listdir
from os.path import isfile, join

def geoh5_create_surface_data(obj_path_dir):

    h5file_path = Path('.') / r"loop.geoh5"

    workspace = Workspace(h5file_path)
    onlyfiles = [f for f in listdir(obj_path_dir) if isfile(join(obj_path_dir, f))]
    
    for file in onlyfiles:
        if ('.obj' in file):
            obj=pd.read_csv(obj_path_dir+'/'+file,' ',names=["code","X","Y","Z"])
            indices=obj[obj['code']=='f']
            vertices=obj[obj['code']=='v']
            vertices=vertices.drop(['code'], axis=1)
            indices=indices[list("XYZ")].astype(int)
            i=indices.to_numpy()-1
            v=vertices.to_numpy()
            
            if(len(i)>0 and len(v)>0):
                # Create a geoh5 surface
                surface = Surface.create(
                    workspace, name=file.replace('.obj',''), vertices=v, cells=i
                )

                workspace.save_entity(surface)
                workspace.finalize()

        
obj_path_dir='../../map2loop2-notebooks/gmd-model/vtkleaflet_2021-06-22-18-26/'
geoh5_create_surface_data(obj_path_dir)

#code to parse a directory of .obj files and combine them into
#a set of Gocad .ts files that GeoscienceAnalyst and Gocad can read
#(note .ts meshes are 1 based)
#Run this code after obj files have been created (see above)

import pandas as pd
from os import listdir
from os.path import isfile, join
import numpy as np

def gocad_create_surface_data(obj_path_dir):


    onlyfiles = [f for f in listdir(obj_path_dir) if isfile(join(obj_path_dir, f))]
    
    for file in onlyfiles:
        if ('.obj' in file):
            obj=pd.read_csv(obj_path_dir+'/'+file,' ',names=["code","X","Y","Z"])
            indices=obj[obj['code']=='f']
            vertices=obj[obj['code']=='v']
            vertices=vertices.drop(['code'], axis=1)
            indices=indices[list("XYZ")].astype(int)
            i=indices.to_numpy()
            v=vertices.to_numpy()
            
            if(len(i)>0 and len(v)>0): 
                fout = open(file.replace('.obj','')+'.ts', "w")
                #fout.write("GOCAD Tsurf 1 \nHEADER {\nname:" + file.replace('.obj','') + "\n}\nTFACE\n")
                fout.write("GOCAD TSurf 1\nHEADER {\nname:"+
                        file.replace('.obj','')+
                        "\n}\nTFACE\n")

                for ind in range(0, v.shape[0]):
                    fout.write("PVRTX %d %f %f %f\n" % (ind + 1, v[ind,0], v[ind,1], v[ind,2]))

                for ind in range(0,i.shape[0]):
                    fout.write("TRGL %d %d %d\n" % (i[ind,0], i[ind,1], i[ind,2]))


                fout.write("END\n")
                fout.close()

            
obj_path_dir='D:\looptests\model_2/'
gocad_create_surface_data(obj_path_dir)

#code to parse a directory of .obj files and combine them into
#a single 3D DXF file that Micromine, Datamine, Vulcan... can read
#(note .dxf meshes are 1 based)
#Run this code after obj files have been created (see above)

import pandas as pd
from os import listdir
from os.path import isfile, join
import numpy as np

def dxf_create_surface_data(obj_path_dir):


    onlyfiles = [f for f in listdir(obj_path_dir) if isfile(join(obj_path_dir, f))]
    
    fout = open('loop.dxf', "w")
    fout.write("  0\nSECTION\n  2\nENTITIES\n")

    for file in onlyfiles:
        if ('.obj' in file):
            obj=pd.read_csv(obj_path_dir+'/'+file,' ',names=["code","X","Y","Z"])
            indices=obj[obj['code']=='f']
            vertices=obj[obj['code']=='v']
            vertices=vertices.drop(['code'], axis=1)
            indices=indices[list("XYZ")].astype(int)
            i=indices.to_numpy()-1
            v=vertices.to_numpy()
           
            if(len(i)>0 and len(v)>0):
                for ind in range(0, i.shape[0]):
                    triangle="  0\n3DFACE\n  8\n{}\n  10\n{}\n  20\n{}\n  30\n{}\n  11\n{}\n  21\n{}\n  31\n{}\n  12\n{}\n  22\n{}\n  32\n{}\n  13\n{}\n  23\n{}\n  33\n{}\n".format(
                                file.replace('.obj',''),v[i[ind,0],0], v[i[ind,0],1], v[i[ind,0],2]
                                                        ,v[i[ind,1],0], v[i[ind,1],1], v[i[ind,1],2]
                                                        ,v[i[ind,2],0], v[i[ind,2],1], v[i[ind,2],2]
                                                        ,v[i[ind,2],0], v[i[ind,2],1], v[i[ind,2],2])
                    fout.write(triangle)
  
    fout.write("0\nENDSEC\n  0\nEOF\n")
    fout.write("END\n")
    fout.close()

            
obj_path_dir='D:\looptests\model_2/'
dxf_create_surface_data(obj_path_dir)





#code to parse a directory of .obj files and combine them into
#a single 3D OMF file that Micromine, Datamine, Vulcan... can read
#(note .omf meshes are 1 based) 
# requires pip install omf (and omfvista and  ipyvtklink if you want to visualise them)
# https://omf.readthedocs.io/en/latest/content/examples.html
# https://gmggroup.org/projects/data-exchange-for-mine-software/
# https://github.com/gmggroup/omf
#Run this code after obj files have been created (see above)

from os import listdir
from os.path import isfile, join
import numpy as np
import omf
import random
import pandas as pd
import copy

def omf_create_surface_data(obj_path_dir):

    proj = omf.Project(
        name='Loop project',
        description='Bunch of surfaces'
    )

    onlyfiles = [f for f in listdir(obj_path_dir) if isfile(join(obj_path_dir, f))]
    
    surfaces=[]
    for file in onlyfiles:
        if ('.obj' in file):

            obj=pd.read_csv(obj_path_dir+'/'+file,' ',names=["code","X","Y","Z"])
            indices=obj[obj['code']=='f']
            vertices=obj[obj['code']=='v']
            vertices=vertices.drop(['code'], axis=1)
            indices=indices[list("XYZ")].astype(int)
            i=indices.to_numpy()-1
            v=vertices.to_numpy()
            i=np.ascontiguousarray(i)
            v=np.ascontiguousarray(v)
            
            if(len(i)>0 and len(v)>0):
                surf = omf.SurfaceElement(
                    name=file.replace('.obj',''),
                    geometry=omf.SurfaceGeometry(
                        vertices=v,
                        triangles=i
                    ),
                    data=[
                        omf.ScalarData(
                            name='rand vert data',
                            array=np.random.rand(v.shape[0]),
                            location='vertices'
                        ),
                        omf.ScalarData(
                            name='rand face data',
                            array=np.random.rand(i.shape[0]),
                            location='faces'
                        )
                        ],           
                    color=[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
                    )
                surfaces.append(copy.deepcopy(surf))

    proj.elements = surfaces

    assert proj.validate()
    
    omf.OMFWriter(proj, 'loop_surf.omf')

            
obj_path_dir='D:\looptests\model_2/'
omf_create_surface_data(obj_path_dir)


#code to take a LoopStructural voxel model and save it out
#as a *.geoh5 GeoscienceAnalyst model 
#weird indexing because default LS block has X & Y swapped & Z -ve
#assumes model already created by LoopStructural, and minx, maxx info from main calculations
#Requires installation of https://github.com/MiraGeoscience/geoh5py 

from pathlib import Path
import numpy as np
from geoh5py.objects import BlockModel
from geoh5py.workspace import Workspace
 
voxel_size=500
sizex=int((maxx-minx)/voxel_size)
sizey=int((maxy-miny)/voxel_size)
sizez=int((model_top-model_base)/voxel_size)
voxels=model.evaluate_model(model.regular_grid(nsteps=(sizey,sizex,sizez),shuffle=False),scale=False)

def create_geoh5_block_model_data(voxels,voxel_size,minx,miny,maxx,maxy,model_base,model_top):

    name = "MyLoopBlockModel"

    # Generate a 3D array

    nodal_y = np.arange(0,maxx-minx+1,voxel_size)
    nodal_x = np.arange(0,maxy-miny+1,voxel_size)
    nodal_z = np.arange(model_top-model_base+1,0,-voxel_size)

    h5file_path = Path('.') / r"loop_block_model.geoh5"


    # Create a workspace
    workspace = Workspace(h5file_path)

    grid = BlockModel.create(
        workspace,
        origin=[minx+(voxel_size/2), miny+(voxel_size/2), model_base+(voxel_size/2)],
        u_cell_delimiters=nodal_x,
        v_cell_delimiters=nodal_y,
        z_cell_delimiters=nodal_z,
        name=name,
        rotation=0,
        allow_move=False,
    )
    data = grid.add_data(
        {
            "DataValues": {
                "association": "CELL",
                "values": (
                    voxels.reshape((nodal_x.shape[0]-1,nodal_y.shape[0]-1,nodal_z.shape[0]-1)).transpose((1,0,2))
                ),
            }
        }
    )
    workspace.save_entity(grid)
    workspace.finalize()
    
create_geoh5_block_model_data(voxels,voxel_size,minx,miny,maxx,maxy,model_base,model_top)



#code to take a LoopStructural voxel model and save it out
#as a *.omf file that Micromine, Datamine, Vulcan... can read
#weird indexing because default LS block has X & Y swapped & Z -ve
# requires pip install omf (and omfvista and  ipyvtklink if you want to visualise them)
# https://omf.readthedocs.io/en/latest/content/examples.html
# https://gmggroup.org/projects/data-exchange-for-mine-software/
# https://github.com/gmggroup/omf
#assumes model already created by LoopStructural, and minx, maxx info from main calculations

import omf
def create_omf_block_model_data(voxels,voxel_size,minx,miny,maxx,maxy,model_base,model_top):

    name = "MyLoopBlockModel"

    # Generate a 3D array
    proj = omf.Project(
        name='Loop project',
        description='Loop Block Model'
    )

    nodal_x = int((maxx-minx+1)/voxel_size)
    nodal_y = int((maxy-miny+1)/voxel_size)
    nodal_z = int((model_top-model_base+1)/voxel_size)
    print(nodal_x,nodal_y,nodal_z)
    print(minx,maxx,miny,maxy,model_base,model_top,voxel_size)
    vol = omf.VolumeElement(
        name='vol',
        geometry=omf.VolumeGridGeometry(
            axis_u=(1,0,0),
            axis_v=(0,1,0),
            axis_w=(0,0,-1),
            tensor_u=np.ones(nodal_y).astype(float)*voxel_size*(nodal_x/nodal_y),
            tensor_v=np.ones(nodal_x).astype(float)*voxel_size*(nodal_y/nodal_x),
            tensor_w=np.ones(nodal_z).astype(float)*voxel_size,
            origin=[minx-(voxel_size/2),miny-(voxel_size/2),model_base-(voxel_size/2)]
        ),
        data=[
            omf.ScalarData(
                name='LithoData',
                location='cells',
                array=voxels.reshape((nodal_z,nodal_x,nodal_y)).transpose((0,1,2)).flatten()
            )
        ]
    )

    proj.elements = [vol]

    assert proj.validate()
    
    omf.OMFWriter(proj, 'loop_block.omf')

create_omf_block_model_data(voxels,voxel_size,minx,miny,maxx,maxy,model_base,model_top)