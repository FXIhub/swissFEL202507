import numpy as np

# load geometry file
geom_fnam = '../geom/JF16M_Bernina_p22263_v1.geom'

def pixel_maps_from_geometry_file(fnam, return_dict = False):
    """
    Return pixel and radius maps from the geometry file

    Input: geometry filename

    Output: x: slab-like pixel map with x coordinate of each slab pixel in the reference system of the detector
            y: slab-like pixel map with y coordinate of each slab pixel in the reference system of the detector
            z: slab-like pixel map with distance of each pixel from the center of the reference system.

    Note:
            ss || y
            fs || x

            vectors should be given by [x, y]
    """
    f = open(fnam, 'r')
    f_lines = []
    for line in f:
        f_lines.append(line)

    keyword_list = ['min_fs', 'min_ss', 'max_fs', 'max_ss', 'fs', 'ss', 'corner_x', 'corner_y']

    detector_dict = {}

    panel_lines = [ x for x in f_lines if '/' in x and 'bad' not in x and not x.startswith(";")]


    for pline in panel_lines:
        items = pline.split('=')[0].split('/')
        if len(items) == 2 :
            panel = items[0].strip()
            property = items[1].strip()
            if property in keyword_list:
                if panel not in detector_dict.keys():
                    detector_dict[panel] = {}
                detector_dict[panel][property] = pline.split('=')[1].split(';')[0].strip()

    parsed_detector_dict = {}

    for p in detector_dict.keys():
        parsed_detector_dict[p] = {}
        parsed_detector_dict[p]['min_fs'] = int( float(detector_dict[p]['min_fs'] ))
        parsed_detector_dict[p]['max_fs'] = int( float(detector_dict[p]['max_fs'] ))
        parsed_detector_dict[p]['min_ss'] = int( float(detector_dict[p]['min_ss'] ))
        parsed_detector_dict[p]['max_ss'] = int( float(detector_dict[p]['max_ss'] ))
        parsed_detector_dict[p]['fs'] = []
        parsed_detector_dict[p]['fs'].append( float( detector_dict[p]['fs'].split('x')[0] ) )
        parsed_detector_dict[p]['fs'].append( float( detector_dict[p]['fs'].split('x')[1].split('y')[0] ) )
        parsed_detector_dict[p]['ss'] = []
        parsed_detector_dict[p]['ss'].append( float( detector_dict[p]['ss'].split('x')[0] ) )
        parsed_detector_dict[p]['ss'].append( float( detector_dict[p]['ss'].split('x')[1].split('y')[0] ) )

        parsed_detector_dict[p]['corner_x'] = float( detector_dict[p]['corner_x'] )
        parsed_detector_dict[p]['corner_y'] = float( detector_dict[p]['corner_y'] )

    max_slab_fs = np.array([parsed_detector_dict[k]['max_fs'] for k in parsed_detector_dict.keys()]).max()
    max_slab_ss = np.array([parsed_detector_dict[k]['max_ss'] for k in parsed_detector_dict.keys()]).max()

    x = np.zeros((max_slab_ss+1, max_slab_fs+1), dtype=np.float32)
    y = np.zeros((max_slab_ss+1, max_slab_fs+1), dtype=np.float32)

    for p in parsed_detector_dict.keys():
        # get the pixel coords for this asic
        i, j = np.meshgrid( np.arange(parsed_detector_dict[p]['max_ss'] - parsed_detector_dict[p]['min_ss'] + 1),
                               np.arange(parsed_detector_dict[p]['max_fs'] - parsed_detector_dict[p]['min_fs'] + 1), indexing='ij')

        #
        # make the y-x ( ss, fs ) vectors, using complex notation
        dx  = parsed_detector_dict[p]['fs'][1] + 1J * parsed_detector_dict[p]['fs'][0]
        dy  = parsed_detector_dict[p]['ss'][1] + 1J * parsed_detector_dict[p]['ss'][0]
        r_0 = parsed_detector_dict[p]['corner_y'] + 1J * parsed_detector_dict[p]['corner_x']
        #
        r   = i * dy + j * dx + r_0
        #
        y[parsed_detector_dict[p]['min_ss']: parsed_detector_dict[p]['max_ss'] + 1, parsed_detector_dict[p]['min_fs']: parsed_detector_dict[p]['max_fs'] + 1] = r.real
        x[parsed_detector_dict[p]['min_ss']: parsed_detector_dict[p]['max_ss'] + 1, parsed_detector_dict[p]['min_fs']: parsed_detector_dict[p]['max_fs'] + 1] = r.imag

    if return_dict :
        return x, y, parsed_detector_dict
    else :
        return x, y


def get_xy_map():
    # pixel size 75e-6 m
    x, y, parsed_detector_dict = pixel_maps_from_geometry_file(geom_fnam, return_dict=True)

    # make panel map
    panel_id = -np.ones(x.shape, dtype=int)
    panel_index_to_name = {}
    index = 0
    for name, panel in parsed_detector_dict.items():
        ss0 = panel['min_ss']
        ss1 = panel['max_ss']+1
        fs0 = panel['min_fs']
        fs1 = panel['max_fs']+1
        panel_id[ss0:ss1, fs0:fs1] = index
        panel_index_to_name[index] = name
        index += 1

    # this is in pixel units
    # xyz = np.zeros((16448, 1030), dtype=float)
    return x, y, panel_id, panel_index_to_name, parsed_detector_dict


def geom_cor(arr):
    x, y = get_xy_map()[:2]
    x0, y0 = x.min(), y.min()
    x = np.round(x-x0).astype(int)
    y = np.round(y-y0).astype(int)
    M = y.max() + 1
    N = x.max() + 1
    out = np.empty((M, N), dtype=arr.dtype)
    out.fill(np.nan)
    out[y, x] = arr
    return out, (y0, x0)

class Geom_cor():

    def __init__(self, dtype):
        x, y = get_xy_map()[:2]
        x0, y0 = x.min(), y.min()
        x -= x0
        y -= y0
        self.x = np.round(x).astype(np.uint16)
        self.y = np.round(y).astype(np.uint16)
        M = int(y.max() + 2)
        N = int(x.max() + 2)
        self.out = np.empty((M, N), dtype=dtype)
        self.out.fill(np.nan)
        self.centre = (y0, x0)

    def get(self, arr):
        self.out[self.y, self.x] = arr
        return self.out
