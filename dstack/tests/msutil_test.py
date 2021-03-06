"""
Unit testing for the msutils module using the unittest module
The test libraries are not part of the module!
Hence, they needs to be handled separately for now.
"""

import os
import unittest
import configparser
import ast

from astropy.coordinates import SkyCoord
from astropy import units as u

import dstack as ds

#Setup the parset file for the unittest
global _PARSET
_PARSET = './unittest_all.in'

def setup_MSutil_unittest(parset_path):
    """For a general unittesting a parset file is used to define the actual MS to test the
    msutil functions against. Thus, any MS can be used for unittesting provided by the user.
    
    The code uses the configparser package to read the config file

    The config section has to be [MSUtil]

    The parset has to contain all variavbles and respective values this function returns.

    Parameters
    ==========
    parset_path: str
        Full path to a parset file defining specific values which can be used for unittesting.
        Hence, local datasets can be used for unittesting.

    Returns
    =======
    MSpath: str
        Full path to a test MS, that is used for unittesting of the utilms functions

    PhaseCentre: Astropy SkyCoord
        The reference phase centre of the MS given as an Astropy SkyCoord object
        Needs to be given in frame='icrs', equinox='J2000' for now

    IDs: list
        The ID of the field and direction of the reference PhaseCentre
    
    NPol: int
        Number of polarizations in the CASAImage
    """
    assert os.path.exists(parset_path), 'Test parset does not exist!'

    config = configparser.ConfigParser()
    config.read(parset_path)

    MSpath = config.get('MSUtil','Mspath')
    assert os.path.isdir(MSpath) == True, 'Invalid input MS is given {0:s}'.format(MSpath)
    
    PhaseCentre = SkyCoord(ra=ast.literal_eval(config.get('MSUtil','PhaseCentre'))[0] * u.rad, 
                dec=ast.literal_eval(config.get('MSUtil','PhaseCentre'))[1] * u.rad,
                frame='icrs', equinox='J2000')
    
    IDs = ast.literal_eval(config.get('MSUtil','IDs'))

    NChan = int(config.get('MSUtil','NChannels'))

    return MSpath, PhaseCentre, IDs, NChan


class TestMSUtil(unittest.TestCase):
    MSpath, PhaseCentre, IDs, NChan = setup_MSutil_unittest(_PARSET)

    def test_get_MS_phasecentre_all(self):
        PhaseCentres = ds.msutil.get_MS_phasecentre_all(self.MSpath)
        assert PhaseCentres[0][0].separation(self.PhaseCentre).arcsec < 1,'Reference PhaseCentre and MS PhaseCentre has >1 arcsec separation!'

    def test_get_single_phasecentre_from_MS(self):
        PhaseCentre = ds.msutil.get_single_phasecentre_from_MS(self.MSpath,field_ID=self.IDs[0],dd_ID=self.IDs[1])
        assert PhaseCentre.separation(self.PhaseCentre).arcsec < 1,'Reference PhaseCentre and MS PhaseCentre has >1 arcsec separation!'

    def test_check_phaseref_in_MS(self):
        found_IDs = ds.msutil.check_phaseref_in_MS(self.MSpath,self.PhaseCentre)
        assert found_IDs[0][0] == self.IDs[0], 'No matching field ID found!'
        assert found_IDs[0][1] == self.IDs[1], 'No matching direction ID found!'

    def test_get_N_chan_from_MS(self):
        C = ds.msutil.get_N_chan_from_MS(self.MSpath)
        assert C == self.NChan, 'Reference and MS channel number is not the same!'

if __name__ == "__main__":
    unittest.main()
