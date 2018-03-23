from PIL import Image
from matplotlib.widgets import LassoSelector
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import path


img = np.asarray(Image.open("img/gymnastics.jpg"))


fig = plt.figure(figsize=(24, 16))
ax = fig.add_subplot(121)
ax.imshow(img)

ax2 = fig.add_subplot(122)
array = np.zeros(img.shape[:-1])
msk = ax2.imshow(array, origin='upper', vmax=2, interpolation='nearest')
print("Image shape", img.shape, array.shape)

xv, yv = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0]))
idx = np.vstack((xv.flatten(), yv.flatten())).T
print('IDX', idx.shape)

lpl = dict(color='blue', linestyle='-', linewidth=5, alpha=0.5)
lpr = dict(color='black', linestyle='-', linewidth=5, alpha=0.5)


def updateArray(array, indices, val):
    a,b = indices.T
    array[b,a] = val
    return array


def select_callback(side='left'):
    val = 1
    if side == 'right':
        val = 2

    def onselect(verts):
        p = path.Path(verts)
        ind = p.contains_points(idx, radius=5)
        v0 = np.array(verts)
        v1 = np.round(verts)
        v2 = np.unique(v1, axis=0)
        print('side:', side)
        # selections
        print(v0.shape, v1.shape, v2.shape, idx[ind].shape)
        global array
        array = updateArray(array, idx[ind], val)
        msk.set_data(array)
        fig.canvas.draw_idle()
    return onselect


lasso_left = LassoSelector(ax, select_callback('left'), lineprops=lpl, button=[1])
lasso_right = LassoSelector(ax, select_callback('right'), lineprops=lpr, button=[3])

plt.show()
