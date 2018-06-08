import matplotlib
import matplotlib.pyplot as plt
import sys
import numpy as np
import nibabel as nib
import scipy
from itertools import cycle
from matplotlib import interactive
import numpy as np
from scipy import ndimage
from scipy.ndimage import binary_dilation, binary_erosion, gaussian_filter, gaussian_gradient_magnitude


## Credit to Morphological Operator Paper

### Default Paramaeters for running as script (Normally get User Input from the API)
#IMG_PATH ='case.nii.gz' ## This is where the user needs to identify the path to image
X_IMG=200
Y_IMG=198
ITERATIONS=400
###


## Hard-coded fixed parameters. 
smoothing=3
lambda1=1
lambda2=1
###

def initiate_contour(shape, center, sqradius, scalerow=1.0):
    grid = np.mgrid[list(map(slice, shape))].T - center
    phi = sqradius - np.sqrt(np.sum((grid.T)**2, 0))
    init_contour = np.float_(phi > 0)
    return init_contour


class op(object):
    
    def __init__(self, iterable):
        """Call functions from the iterable each time it is called."""
        self.funcs = cycle(iterable)
    
    def __call__(self, *args, **kwargs):
        f = next(self.funcs)
        return f(*args, **kwargs)

A = [np.eye(3), np.array([[0,1,0]]*3), np.flipud(np.eye(3)), np.rot90([[0,1,0]]*3)]
B = [np.zeros((3,3,3)) for i in range(9)]

B[0][:,:,1] = 1
B[1][:,1,:] = 1
B[2][1,:,:] = 1
B[3][:,[0,1,2],[0,1,2]] = 1
B[4][:,[0,1,2],[2,1,0]] = 1
B[5][[0,1,2],:,[0,1,2]] = 1
B[6][[0,1,2],:,[2,1,0]] = 1
B[7][[0,1,2],[0,1,2],:] = 1
B[8][[0,1,2],[2,1,0],:] = 1

_aux = np.zeros((0))


def SI(u):
    """SI operator."""
    global _aux
    if np.ndim(u) == 2:
        P = A
    elif np.ndim(u) == 3:
        P = B
    if u.shape != _aux.shape[1:]:
        _aux = np.zeros((len(P),) + u.shape)
    
    for _aux_i, P_i in zip(_aux, P):
        _aux_i[:] = binary_erosion(u, P_i)
    
    return _aux.max(0)

def IS(u):
    """IS operator."""
    global _aux
    if np.ndim(u) == 2:
        P = A
    elif np.ndim(u) == 3:
        P = B
    if u.shape != _aux.shape[1:]:
        _aux = np.zeros((len(P),) + u.shape)
    
    for _aux_i, P_i in zip(_aux, P):
        _aux_i[:] = binary_dilation(u, P_i)
    
    return _aux.min(0)

def run(img_path, x_img, y_img, iterations, redraw_contour):
    ex_img=nib.load(img_path).get_data()

    ex_img=ex_img.T


    ex_nn_mask= initiate_contour(ex_img.shape, (x_img, y_img), 20)


    SI_IS = lambda u: SI(IS(u))
    IS_SI = lambda u: IS(SI(u))
    curvop = op([SI_IS, IS_SI])


    levelset=ex_nn_mask
    mask = np.double(levelset)
    mask[levelset>0]=1
    mask[levelset<=0]=0


    #plt.ion()
    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #plt.imshow(ex_img, cmap=plt.cm.gray)
    #plt.show()


    for i in range(iterations):
    
        inside = mask>0
        outside = mask<=0


        c0 = ex_img[outside].sum() / float(outside.sum())
        c1 = ex_img[inside].sum() / float(inside.sum())

            # Image attachment.
        dres = np.array(np.gradient(mask))

        abs_dres = np.abs(dres).sum(0)

        aux = abs_dres * (lambda1*(ex_img - c1)**2 - lambda2*(ex_img - c0)**2)
    
        aux.shape

        res = np.copy(mask)
        res[aux < 0] = 1
        res[aux > 0] = 0
    
        for j in range(smoothing):
            res = curvop(res)    
        mask=res

        if i%10==0:
            redraw_contour(res)

def main():
    run(IMG_PATH, X_IMG, Y_IMG, ITERATIONS)

if __name__ == '__main__':
    main()
