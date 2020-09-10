"""
Collection of utility functions to interact with CASA images. 
Grids are currently dumped in casaimage format, hence the utilities works at both images and grids.
"""

__all__ = ['get_N_chan_from_CIM', 'get_N_pol_from_CIM', 'check_CIM_equity']

import numpy as np

from casacore import images as casaimage


def get_N_chan_from_CIM(cimpath):
    """Get the number of channels from a CASAImage

    CASAImage indices: [freq, Stokes, x, y]

    Parameters
    ==========
    cimpath: str
        The input CASAImage parth
    
    Returns
    =======
    N_chan: int
        Number of channels in the CASAImage
    """
    cim = casaimage.image(cimpath)
    assert cim.ndim() == 4, 'The image has more than 4 axes!'

    N_chan = np.shape(cim.getdata())[0]

    return N_chan

def get_N_pol_from_CIM(cimpath):
    """Get the number of polarisations from a CASAImage. Note, that the
    polarisation type is not returned!

    CASAImage indices: [freq, Stokes, x, y]

    Parameters
    ==========
    cimpath: str
        The input CASAImage parth
    
    Returns
    =======
    N_pol: int
        Number of polarisations in the CASAImage
    """
    cim = casaimage.image(cimpath)
    assert cim.ndim() == 4, 'The image has more than 4 axes!'

    N_pol = np.shape(cim.getdata())[1]

    return N_pol

def check_CIM_equity(cimpath_a,cimpath_b,numprec=1e-8):
    """Check if two CASAImages are identical or not up to a defined numerical precision
    This function is used to test certain piepline features.

    Note: NaN-s are trethed as equals, and the :numprec: parameter only sets the relative difference limit.

    Parameters
    ==========
    cimpath_a: str
        The input CASAImage parth of Alice

    cimpath_b: str
        The input CASAImage parth of Bob

    numprec: float
        The numerical precision limit of the maximum allowed relative
        difference between CASAImages Alice and Bob.
        If set to zero, equity is checked.

    Returns
    =======
    equity: bool
        True or False, base on the equity of Alice and Bob
    """

    cimA = casaimage.image(cimpath_a)
    cimB = casaimage.image(cimpath_b)

    assert cimA.ndim() == cimB.ndim(), 'The dimension of the two input CASAImage is not equal!'

    if numprec == 0.:
        return np.array_equiv(cimA.getdata(),cimB.getdata())
    else:
        return np.allclose(cimA.getdata(),cimB.getdata(),atol=0,rtol=numprec,equal_nan=True)


if __name__ == "__main__":
    pass