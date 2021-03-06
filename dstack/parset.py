"""
This module is a wrapper around parsets used in YandaSoft.
The code takes template parset(s) and creates custom parsets for pipelines such as the gridded DINGO pipeline.
Currently not everything is supported and the wrapper is not complete, i.e. the user can break the wrapper if not careful!
"""

__all__ = ['list_supported_parset_settings', 'create_parset_mapping',
            'check_preconditioner_suppoort', 'check_parameter_and_Imager_compatibility', 
            'check_parameter_and_Preconditioner_compatibility', 
            'check_parameter_and_Gridder_compatibility', 'Parset']

import os
import logging

#=== Setup logging ===
log = logging.getLogger(__name__)

#=== Globals ===
global _SUPPORTED_IMAGERS
global _SUPPORTED_SOLVERS
global _SUPPORTED_GRIDDER_NAMES
global _SUPPORTED_PRECONDITIONERS

_SUPPORTED_IMAGERS = ['Cimager', 'Cdeconvolver', 'dstack']
_SUPPORTED_SOLVERS = ['Clean']
_SUPPORTED_GRIDDER_NAMES = ['Box', 'SphFunc', 'WStack', 'WProject']
_SUPPORTED_PRECONDITIONERS = ['Wiener','GaussianTaper']

#Some default parameters
global _DEFAULT_IMAGER
global _DEFAULT_IMAGE_NAMES
global _DEFAULT_GRIDDER_NAME
global _DEFAULT_PRECONDITIONER

_DEFAULT_IMAGER = 'Cimager'
_DEFAULT_IMAGE_NAMES = 'image.dstack.test'
_DEFAULT_GRIDDER_NAME = 'WProject'
_DEFAULT_PRECONDITIONER = []

#Globals defining the compatibility of different Preconditioners
global _FORBIDDEN_WITH_NO_PRECONDITIONING
global _WIENER_FORBIDDEN_PARAMS
global _GAUSSIANTAPER_FORBIDDEN_PARAMS

_FORBIDDEN_WITH_NO_PRECONDITIONING = ['Preservecf', 'PGaussianTaper']
_WIENER_FORBIDDEN_PARAMS = ['PWnoisepower', 'PWnormalise', 'PWrobustness', 'PWtaper']
_GAUSSIANTAPER_FORBIDDEN_PARAMS = ['PGTisPsfSize', 'PGTtolerance']

#Globals defining the compatibility of different gridders
global _COPLANAR_FORBIDDEN_PARAMS
global _NON_ANTIALIASING_FORBIDDEN_PARAMS

#Forbidden for gridders not taking the w-term into account
#Basically everything except WProject and Wstack (currently including parameters supporting Non-linear sampling in w-space)
_COPLANAR_FORBIDDEN_PARAMS = ['GNwmax', 'GNwmaxclip', 'GNnwplanes', 'GNwstats', 'GNwsampling', 'GNWexponent', 'GNWnwplanes50', 
                                'GNWexport', 'GNcutoff', 'GNCabsolute', 'GNoversample', 'GNmaxsupport', 'GNlimitsupport',
                                'GNvariablesupport', 'GNoffsetsupport', 'GNtablename', 'GNusedouble', 'GNsharecf'] 
_NON_ANTIALIASING_FORBIDDEN_PARAMS = ['GNalpha'] #Forbidden params for everything except SphFunc and WProject

#=== Functions ===
def list_supported_parset_settings():
    """List the ``YandaSoft`` parset settings that are currently supported by ``dstack``.

    This function uses logger level INFO to return the supported settings

    Parameters
    ==========

    Returns
    =======
    Prints out the supported settings: log
    """
    print_support = lambda functionality, flist: log.info('Supported {0:s}: '.format(functionality) + ' '.join(map(str, flist)))

    log.info('Settings for YandaSoft parsets supported by the dstack wrapper:')
    print_support('Imagers',_SUPPORTED_IMAGERS)
    print_support('Solvers',_SUPPORTED_SOLVERS)
    print_support('Gridders',_SUPPORTED_GRIDDER_NAMES)
    print_support('Preconditioners',_SUPPORTED_PRECONDITIONERS)


def create_parset_mapping(image_names=_DEFAULT_IMAGE_NAMES, gridder_name=_DEFAULT_GRIDDER_NAME):
    """This function creates a mapping between the ``dstack`` and ``YandaSoft`` parset variables.
    The imager used is not included in the ``YandaSoft`` variables. However, when reading in a template parset
    using the ``__init__()`` method of the Parset class, the imager name have to be included in the parset file.
    This solution gives more flexibility with reading and creating parsets. The list of supported imagers:

    - Cimager
    - Cdeconvolver

    And for reading the template parset, a special imager name is allowed: dstack (not allowed for creating parsets)

    This function however, just defines the mapping between the ``dstack`` and ``YandaSoft`` and thus can be used to
    overwrite an existing mapping of a ``Parset``. This is useful when a ``Parset`` has already created from a template,
    but we want to modify some values and create a parset that uses a different imager.

    Currently not all parset parameters are supported.
    e.g. only the Clean solvers are supported in the current version of ``dstcak``

    The mapping uses the ``Python 3.7+`` feature that dictionaries sorted as they created.
    I.e. the mapping is sorted as it is hard-coded in this function!

    Parameters
    ==========
    image_names: str, optional
        The ``Names`` parameter of ``YandaSoft`` imager task. The code *currelntly not supporting a list of Names only a single Name can be used*!

    gridder_name: str, optional
        The ``gridder`` parameter of ``YandaSoft`` imager task.

    Returns
    =======
    parset_mapping: dict
        The dictionary that is the mapping between the ``dstack`` and ``YandaSoft`` parset variables
    inverse_parset_mapping: dict
        Inverse dictionary of ``parset_mapping``
    """
    parset_mapping = {
        #Basic parameters
        'dataset': 'dataset',
        'grid' : 'grid',
        'psfgrid' : 'psfgrid',
        'pcf' : 'pcf',
        'imagetype' : 'imagetype',
        'nworkergroups' : 'nworkergroups',
        'nchanpercore' : 'nchanpercore',
        'Channels' : 'Channels',
        'Frequencies' : 'Frequencies',
        'beams' : 'beams',
        'nwriters' : 'nwriters',
        'freqframe' : 'freqframe',
        'singleoutputfile' : 'singleoutputfile',
        'solverpercore' : 'solverpercore',
        'datacolumn' : 'datacolumn',
        'sphfuncforpsf' : 'sphfuncforpsf',
        'calibrate' : 'calibrate',
        'Cscalenoise' : 'calibrate.scalenoise',
        'Callowflag' : 'calibrate.allowflag',
        'Cignorebeam' : 'calibrate.ignorebeam',
        'gainsfile' : 'gainsfile',
        'residuals' : 'residuals',
        'restore' : 'restore',
        'nUVWMachines' : 'nUVWMachines',
        'uvwMachineDirTolerance' : 'uvwMachineDirTolerance',
        'MaxUV' : 'MaxUV',
        'MinUV' : 'MinUV',
        'usetmpfs' : 'usetmpfs',
        'tmpfs' : 'tmpfs',
        'rankstoringcf' : 'rankstoringcf',
        'visweights' : 'visweights',
        'VMFSreffreq' : 'visweights.MFS.reffreq',
        'ncycles' : 'ncycles',
        'sensitivityimage' : 'sensitivityimage',
        'Scutoff' : 'sensitivityimage.cutoff',
        'channeltolerance' : 'channeltolerance',
        'dumpgrids' : 'dumpgrids',
        'memorybuffers' : 'memorybuffers',
        #Images settings
        'Ireuse' : 'Images.reuse',
        'Ishape' : 'Images.shape',
        'Idirection' : 'Images.direction',
        'Icellsize' : 'Images.cellsize',
        'IwriteAtMajorCycle' : 'Images.writeAtMajorCycle',
        'IrestFrequency' : 'Images.restFrequency',
        'INames' : 'Images.Names',
        'INnchan' : 'Images.{0:s}.nchan'.format(image_names),
        'INfrequency' : 'Images.{0:s}.frequency'.format(image_names),
        'INdirection' : 'Images.{0:s}.direction'.format(image_names),
        'INtangent' : 'Images.{0:s}.tangent'.format(image_names),
        'INewprojection' : 'Images.{0:s}.ewprojection'.format(image_names),
        'INshape' : 'Images.{0:s}.shape'.format(image_names),
        'INcellsize' : 'Images.{0:s}.cellsize'.format(image_names),
        'INnfacets' : 'Images.{0:s}.nfacets'.format(image_names),
        'INpolarisation' : 'Images.{0:s}.polarisation'.format(image_names),
        'INnterms' : 'Images.{0:s}.nterms'.format(image_names),
        'INfacetstep' : 'Images.{0:s}.facetstep'.format(image_names),
        #Gridding setup
        'gridder' : 'gridder',
        'Gpadding' : 'gridder.padding',
        'Galldatapsf' : 'gridder.alldatapsf',
        'Goversampleweight' : 'gridder.oversampleweight',
        'GMaxPointingSeparation' : 'gridder.MaxPointingSeparation',
        'Gsnapshotimaging' : 'gridder.snapshotimaging',
        'GSwtolerance' : 'gridder.snapshotimaging.wtolerance',
        'GSclipping' : 'gridder.snapshotimaging.clipping',
        'GSweightsclipping' : 'gridder.snapshotimaging.weightsclipping',
        'GSreprojectpsf' : 'gridder.snapshotimaging.reprojectpsf',
        'GScoorddecimation' : 'gridder.snapshotimaging.coorddecimation',
        'GSinterpmethod' : 'gridder.snapshotimaging.interpmethod',
        'GSlongtrack' : 'gridder.snapshotimaging.longtrack',
        'Gbwsmearing' : 'gridder.bwsmearing',
        'GBchanbw' : 'gridder.bwsmearing.chanbw',
        'GBnsteps' : 'gridder.bwsmearing.nsteps',
        'Gparotation' : 'gridder.parotation',
        'GPangle' : 'gridder.parotation.angle',
        'Gswappols' : 'gridder.swappols',
        'GNwmax' : 'gridder.{0:s}.wmax'.format(gridder_name),
        'GNwmaxclip' : 'gridder.{0:s}.wmaxclip'.format(gridder_name),
        'GNnwplanes' : 'gridder.{0:s}.nwplanes'.format(gridder_name),
        'GNwstats' : 'gridder.{0:s}.wstats'.format(gridder_name),
        'GNalpha' : 'gridder.{0:s}.alpha'.format(gridder_name),
        'GNwsampling' : 'gridder.{0:s}.wsampling'.format(gridder_name),
        'GNWexponent' : 'gridder.{0:s}.wsampling.exponent'.format(gridder_name),
        'GNWnwplanes50' : 'gridder.{0:s}.wsampling.nwplanes50'.format(gridder_name),
        'GNWexport' : 'gridder.{0:s}.wsampling.export'.format(gridder_name),
        'GNcutoff' : 'gridder.{0:s}.cutoff'.format(gridder_name),
        'GNCabsolute' : 'gridder.{0:s}.cutoff.absolute'.format(gridder_name),
        'GNoversample' : 'gridder.{0:s}.oversample'.format(gridder_name),
        'GNmaxsupport' : 'gridder.{0:s}.maxsupport'.format(gridder_name),
        'GNlimitsupport' : 'gridder.{0:s}.limitsupport'.format(gridder_name),
        'GNvariablesupport' : 'gridder.{0:s}.variablesupport'.format(gridder_name),
        'GNoffsetsupport' : 'gridder.{0:s}.offsetsupport'.format(gridder_name),
        'GNtablename' : 'gridder.{0:s}.tablename'.format(gridder_name),
        'GNusedouble' : 'gridder.{0:s}.usedouble'.format(gridder_name),
        'GNsharecf' : 'gridder.{0:s}.sharecf'.format(gridder_name),
        #Deconvolutoin solver
        'solver' : 'solver',
        'Cverbose' : 'solver.Clean.verbose',
        'Ctolerance' : 'solver.Clean.tolerance',
        'Cweightcutoff' : 'solver.Clean.weightcutoff',
        'Ccweightcutoff' : 'solver.Clean.weightcutoff.clean',
        'Calgorithm' : 'solver.Clean.algorithm',
        'Cscales' : 'solver.Clean.scales',
        'Cniter' : 'solver.Clean.niter',
        'Cgain' : 'solver.Clean.gain',
        'Cbeam' : 'solver.Clean.beam',
        'Cspeedup' : 'solver.Clean.speedup',
        'Cpadding' : 'solver.Clean.padding',
        'Csolutiontype' : 'solver.Clean.solutiontype',
        'Clogevery' : 'solver.Clean.logevery',
        'Csaveintermediate' : 'solver.Clean.saveintermediate',
        'CBpsfwidth' : 'solver.Clean.psfwidth',
        'CBdetectdivergence' : 'solver.Clean.detectdivergence',
        'CBorthogonal' : 'solver.Clean.orthogonal',
        'CBdecoupled' : 'solver.Clean.decoupled',
        'Tminorcycle' : 'threshold.minorcycle',
        'Tmajorcycle' : 'threshold.majorcycle',
        'Tmasking' : 'threshold.masking',
        #Preconditioning
        'PNames' : 'preconditioner.Names',
        'Preservecf' : 'preconditioner.preservecf',
        'PWnoisepower' : 'preconditioner.Wiener.noisepower',
        'PWnormalise' : 'preconditioner.Wiener.normalise',
        'PWrobustness' : 'preconditioner.Wiener.robustness',
        'PWtaper' : 'preconditioner.Wiener.taper',
        'PGaussianTaper' : 'preconditioner.GaussianTaper',
        'PGTisPsfSize' : 'preconditioner.GaussianTaper.isPsfSize',
        'PGTtolerance' : 'preconditioner.GaussianTaper.tolerance',
        #Restoring cycles
        'Rbeam' : 'restore.beam',
        'Rbeamcutoff' : 'restore.beam.cutoff',
        'Requalise' : 'restore.equalise',
        'Rupdateresiduals' : 'restore.updateresiduals',
        'RbeamReference' : 'restore.beamReference'
    }

    inverse_parset_mapping = {v: k for k, v in parset_mapping.items()}

    return parset_mapping, inverse_parset_mapping

#Generate the mapping order:
#        A dictionary defines the order of ``dstack`` parset parameters in which they
#        written out to prompt or to file.
log.debug('Create _MAPPING_ORDER global variable')
_MAPPING_ORDER = {k: i for i, k in zip(enumerate(create_parset_mapping()[0]),create_parset_mapping()[0])}

#Define ambigous imaging parameters
_AMBIGOUS_IMAGING_PARAMETERS = {'Ishape' : 'INshape',
                                'Idirection' : 'INdirection',
                                'Icellsize' : 'INcellsize'}

def check_preconditioner_suppoort(preconditioners=_DEFAULT_PRECONDITIONER):
    """Check if the list of preconditioners given is supported

    Parameters
    ==========
    preconditioners: list
        A list containing the preconditioners to test

    Returns
    =======
    allowded: bool, optional
        True, if the given list contains only allowed preconditioners,
        and False if not
    """
    if preconditioners == []:
        return True
    else:
        for preconditioner in preconditioners:
            if preconditioner not in _SUPPORTED_PRECONDITIONERS:
                return False
    return True

def check_parameter_and_Imager_compatibility(parset_param, imager=_DEFAULT_IMAGER):
    """This function defines which parameters the supported imagers are not compatible with.

    This check returns False if the given parameter is not compatible with the imager

    This function is only called when a parset is written to disc. The in-memory parest
    can be really messed up for sake of flexibility

    Parameters
    ==========
    parset_param: str
        The ``dstack`` parset parameter variable name

    imager: str, optional
        Imager to test against

    Returns
    =======
    Compatibility: bool
        True if the parameter is allowed with the given imager,
        and False if not
    """
    if imager not in _SUPPORTED_IMAGERS:
        raise TypeError('Imager {0:s} is not supported!'.format(imager))

    if imager == 'Cimager':
        forbidden_params = ['grid','psfgrid','pcf']

        if parset_param in forbidden_params:
            return False
        else:
            return True
    elif imager == 'Cdeconvolver':
        forbidden_params = ['dataset']

        if parset_param in forbidden_params:
            return False
        else:
            return True
    else:
        #Everything goes with the dstack imager :O
        return True

def check_parameter_and_Preconditioner_compatibility(parset_param, preconditioners=_DEFAULT_PRECONDITIONER):
    """This function defines which parameters the preconditioners used are not compatible with.

    This check returns False if the given parameter is not compatible with the preconditioner used.

    This function is only called when a parset is written to disc. The in-memory parest
    can be really messed up for sake of flexibility.

    Parameters
    ==========
    parset_param: str
        The ``dstack`` parset parameter variable name

    preconditioners: list, optional
        This is the list of preconditioners used

    Returns
    =======
    Compatibility: bool
        True if the parameter is allowed with the given preconditioner(s),
        and False if not
    """
    if preconditioners == []:
        #The Ppreservecf parameter is allowed due to the misterious ways YandaSoft works...
        #However, I decided not to allow any preconditioning-related parameters in this case,
        #as this solution allows to make Cdeconvolver running with no-preconditioning option by default
        #if the preconditioner is set to []
        if parset_param in _FORBIDDEN_WITH_NO_PRECONDITIONING + _WIENER_FORBIDDEN_PARAMS + _GAUSSIANTAPER_FORBIDDEN_PARAMS:
            return False
        else:
            return True
    elif 'Wiener' not in preconditioners:
        if parset_param in _WIENER_FORBIDDEN_PARAMS:
            return False
        else:
            return True
    elif 'GaussianTaper' not in preconditioners:
        if parset_param in _GAUSSIANTAPER_FORBIDDEN_PARAMS:
            return False
        else:
            return True
    else:
        if check_preconditioner_suppoort(preconditioners) == False:
            raise TypeError('The preconditioner given is not supported!')
        return True

def check_parameter_and_Gridder_compatibility(parset_param, gridder_name=_DEFAULT_GRIDDER_NAME):
    """This function defines which parameters the gridder used not compatible with.

    This check returns False if the given parameter is not compatible with the gridder used.

    This function is only called when a parset is written to disc. The in-memory parest
    can be really messed up for sake of flexibility.

    Parameters
    ==========
    parset_param: str
        The ``dstack`` parset parameter variable name

    gridder_name: str, optional
        This is the name of the gridder used

    Returns
    =======
    Compatibility: bool
        True if the parameter is allowed with the given gridder(,
        and False if not
    """
    if gridder_name == 'Box':
        if parset_param in _COPLANAR_FORBIDDEN_PARAMS + _NON_ANTIALIASING_FORBIDDEN_PARAMS:
            return False
        else:
            return True
    elif gridder_name == 'SphFunc':
        if parset_param in _COPLANAR_FORBIDDEN_PARAMS:
            return False
        else:
            return True
    elif gridder_name == 'WStack':
        if parset_param in _NON_ANTIALIASING_FORBIDDEN_PARAMS:
            return False
        else:
            return True
    elif gridder_name == 'WProject':
        return True
    else:
        if gridder_name not in _SUPPORTED_GRIDDER_NAMES:
            raise TypeError('The gridder given is not supported!')
        return True

#=== CLASSES ===
class Parset(object):
    """Creates an in-memory dictionary of a ``YandaSoft`` parameterset.

    It can be initialized as an empty dictionary and then the user can define
    *every* parameter. Or a template parset can be used to initialize the
    imaging parameters. To build different imaging parsets for pipelines,
    the variation of the two methods is advised.

    The template parset has to have each parameter in a new line starting with
    the ``YandaSoft`` parameter e.g. ``Cimgaer.dataset``, which obviously starts
    with the imager name. See the list of imagers supported in  ``create_parset_mapping()``
    The parameters value is the string after = and a backspace until the end of the line.

    Lines starting with ``#`` are skipped.

    The mapping between ``dstack`` and ``YandaSoft`` variables is defined by
    the dictionary created with ``create_parset_mapping`.

    The mapping is an attribute of the ``Parset`` class.

    The mapping is based on the ``ASKAPSOFT`` `documentation <https://www.atnf.csiro.au/computing/software/askapsoft/sdp/docs/current/calim/index.html>`_

    Though the ``Parset`` class offers a range of flexibility, currently the template parset
    have to consist only one Images Names and gridder. These must be specified when creating 
    a ``Parset`` object and the template have to use the given naming convention in order to
    be compatible with the mapping generated.

    If no template is given, an empty parset is generated.

    Keyword Arguments
    =================
    imager: str
        Have to be a selected ``YandaSoft`` Imager task. When a parset file is created
        this attribute is used to define the imager

    image_names: str
        The ``Names`` parameter of the parset. The template parset has to have this ``Names``
        parameters (if used), when read in. Nevertheless, this can be changed on the fly, and
        parsets with different names can be created. Use the ``update_parset_mapping()`` function
        for this.

    gridder_name: str
        The ``gridder`` parameter of ``YandaSoft`` imager task.

    template_path: str or None, optional
        Full path to a template parset file, which can be used to 
        initialize the parset parameters

    preconditioner: list or None, optional
        The preconditioner(s) used when saving the parset. The ``Parset`` object is designed to be
        flexible, allowing for parameters coexist even if it would make no sense. However, when 
        saving a Parset, a series of check ensures that the parset is compatible with ``YandaSoft``.
        The solution for preconditioning is that the user can define which preconditioner to use
        when saving a parset. This argument enable the user to define what preconditioners to use
        when saving the parset. If set to None, the preconditioners are read from the template if given.
        It creates an empty list if no template is given or if the template defines no preconditioning.
        Note, that if the template uses preconditioning not supported by ``dstack``, it will be ignored.
    """
    def __init__(self, imager=_DEFAULT_IMAGER, image_names=_DEFAULT_IMAGE_NAMES, gridder_name=_DEFAULT_GRIDDER_NAME, template_path=None, preconditioner=None):
        log.debug('Initialize new Parset object:')
        object.__setattr__(self, "_parset", {})

        if imager not in _SUPPORTED_IMAGERS:
            raise TypeError('Imager {0:s} is not supported!'.format(imager))

        if gridder_name not in _SUPPORTED_GRIDDER_NAMES:
            raise TypeError('Gridder {0:s} is not supported!'.format(gridder_name))

        self._imager = imager
        self._image_names = image_names
        self._gridder_name = gridder_name

        #Set up an empty list for ._preconditioner =>  I will fill this up with the preconditioner from the template file
        if preconditioner != None:
            if check_preconditioner_suppoort(preconditioner) == False:
                raise TypeError('The preconditioner given is not allowed!')
            else:
                user_defined_preconditioner = True
        else:
            user_defined_preconditioner = False
        self._preconditioner = []

        pm, ipm = create_parset_mapping(image_names=self._image_names,gridder_name=self._gridder_name)
        object.__setattr__(self,"_mapping", pm)
        object.__setattr__(self,"_inverse_mapping", ipm)

        if template_path != None:
            if os.path.exists(template_path) == False:
                raise NameError('Template parset does not exist: {0:s}'.format(template_path))

            log.info('Create Parset based on template: {0:s}'.format(template_path))

            with open(template_path, 'r') as f:
                log.debug('Reading in template Parset file: {0:s}'.format(template_path))
                for line in f.readlines():
                    if line[0] == '#' or line.split() == []:
                        continue
                    
                    name = line.split()[0]

                    #Check if the name starts with a string from the list of supported imagers
                    if list(filter(name.startswith, _SUPPORTED_IMAGERS)) != []:
                        name = '.'.join(name.split('.')[1:])#Name without imager
                        value = line[line.index('= ')+2:].rstrip()#get rid of line separators with .rstrip()

                        if name not in self._inverse_mapping:
                            raise TypeError('Can not interpret the parameter {0:s} given in the parset {1:s}!'.format(
                                            name,template_path))
                        
                        #Some consistency check
                        if self._inverse_mapping[name] == 'INames':
                            if self._image_names not in value:
                                raise NameError('Parsed created with different image names ({0:s}) from that defined in the template parset {1:s}!'.format(
                                    self._image_names,template_path))

                        if self._inverse_mapping[name] == 'gridder':
                            if self._gridder_name not in value:
                                raise NameError('Parsed created with different gridder name ({0:s}) from that defined in the template parset {1:s}!'.format(
                                self._gridder_name,template_path))

                        if self._inverse_mapping[name] == 'solver':
                            if value not in  _SUPPORTED_SOLVERS:
                                raise NameError('The solver defined in the template {0:s} is not supported!'.format(template_path))

                        if self._inverse_mapping[name] == 'PNames':
                            valid_preconditioner = False

                            if ''.join(value.split()) == '[]':
                                valid_preconditioner = True
                            else:
                                for p in _SUPPORTED_PRECONDITIONERS:
                                    if p in value:
                                        valid_preconditioner = True

                                        #Add the preconditioner to the list
                                        self.add_preconditioner(p)

                            if valid_preconditioner == False:
                                raise NameError('The preconditioner defined in the template {0:s} is not supported!'.format(
                                                template_path))

                            self._parset[self._inverse_mapping[name]] = self._preconditioner
                            continue

                        self._parset[self._inverse_mapping[name]] = value
                        log.debug('Parset parameter added: {0:s} = {1:s}'.format(self._inverse_mapping[name],value))
                    
                    else:
                        log.warning('Invalid parset parameter: {0:s} as the imager used is {1:s}! (parameter skipped)'.format(
                        name,self._imager,template_path))

            #Set up the Nnames key in the _parameters as it always have to exist in otder to save the Parset with correct preconditioning settings!
            if 'PNames' not in self._parset.keys():
                self._parset['PNames'] = []
            elif isinstance(self._parset['PNames'],list) == False:
                self._parset['PNames'] = eval(self._parset['PNames']) #Evaluate string input as a list             

            #Now I overwrite the ._preconditioner attribute with the preconditioner defined by the user if given
            if user_defined_preconditioner == True:
                del self._preconditioner
                self._preconditioner = preconditioner

            #Oreder params according to mapping!
            self.sort_parset()

            log.info('Parset attributes: imager = {0:s}; image_names = {1:s}; gridder_name = {2:s}; preconditioner = {3:s}'.format(
                    self._imager, self._image_names, self._gridder_name, str(self._preconditioner)))

        else:
            self._parset[self._inverse_mapping[self._mapping['INames']]] = self._image_names
            self._parset[self._inverse_mapping[self._mapping['gridder']]] = self._gridder_name
            log.info('Create Parset without template parset and parameters: Inames = {0:s}; gridder = {1:s}'.format(
                        self._image_names,self._gridder_name))
            log.info('Parset attributes: imager = {0:s}; image_names = {1:s}; gridder_name = {2:s}; preconditioner = {3:s}'.format(
                    self._imager, self._image_names, self._gridder_name, str(self._preconditioner)))

    def add_parset_parameter(self,name,value):
        """Add a new Parset parameter to the _parset attribute

        This is the preferred method to add parameters to the parset.

        Parameters
        ==========
        name: str
            Name of the parameter. Have to be in ``self._mapping`` keys.

        value: str (or almost anything)
            The value of the parameter. When the ``Parset`` is saved
            the value will be converted to a string.

        Returns
        =======
        :obj:`Parset`
            The ``_parset`` dict is appended with the ``name`` and ``value``
        """
        if name not in set(self._mapping.keys()): 
            log.info('Skip adding invalid parset paremater: {0:s}'.format(name))
        else:
            log.debug('Add parset parameter: {0:s}'.format(name))
            self._parset[self._inverse_mapping[self._mapping[name]]] = value

    def remove_parset_parameter(self,name):
        """Remove a parset parameter from the _parset attribute

        This is the preferred method to remove parameters.

        Parameters
        ==========
        name: str
            Name of the parameter. Have to be in ``self._mapping`` keys.

        Returns
        =======
        :obj:`Parset`
            The ``_parset`` dict is without with the element called ``name``
        """
        if name not in set(self._mapping.keys()): 
            log.info('Can not remove invalid parset parameter: {0:s}'.format(name))
        else:
            try:
                del self._parset[name]
                log.debug('Parameter removed from parset: {0:s}'.format(name))
            except  KeyError:
                log.info('Parset do not contain parameter: {0:s}'.format(name))

    def __setattr__(self, name, value):
        """Add a new key and a corresponding value to the ``Parset``

        Parameters
        ==========
        name: str
            Name of the parameter. Have to be in ``self._mapping`` keys.

        value: str (or almost anything)
            The value of the parameter. When the ``Parset`` is saved
            the value will be converted to a string.

        Returns
        =======
        :obj:`Parset`
            The ``_parset`` dict is appended with the ``name`` and ``value``
        """
        custom_attributes = ['_parset', '_imager','_image_names', '_gridder_name','_preconditioner','_mapping','_inverse_mapping']
        if name in custom_attributes:
            object.__setattr__(self, name, value)
        else:
            self.add_parset_parameter(name,value)

    def __repr__(self):
        """Return the ``_parset`` dict as a line-by line string of keys and values."""
        self.sort_parset() #To make it fancy and slow :O
        lines = 'Imager: {0:s}\n'.format(self._imager)
        lines += 'Image Names: {0:s}\n'.format(self._image_names)
        lines += 'Preconditioner: {}\n'.format(self._preconditioner)
        lines += 'Parset parameters:\n{\n'
        for key, value in self._parset.items():
            lines += '\t{} = {}\n'.format(key, value)
        lines += '}'
        return lines

    def set_image_names_param_consistency(self,param,use_image_names=False):
        """When saving a parset, ambigous Images parameters should not be allowed.

        However, some parameters of Images can be defined two ways:
            a) ``Images.parameter``
            b) ``Images.image_name.parameter``

        The ``Parset`` calls allows the user to define both parameters,
        for flexibility. Nevertheless, in saving the parset the parameters
        should be consistent.

        This function checks for consistency in the ambigous parameters
        of the Images.parameters and if the parameter is ambigous it
        returns the name defined by either a) or b) options.

        I.e. The function takes a key and if it is ambigous it returns
        the key of the user-defined key which corresponding value should be used
        for both parameters when writing out the parameters

        This function uses the ``_AMBIGOUS_IMAGING_PARAMETERS`` dictionary
        to check if the parameter given is really ambigous.

        Parameters
        ==========
        param: str
            The parameter name in the mapping that ambiguity should be checked.
            If not in ``_AMBIGOUS_IMAGING_PARAMETERS``, the function returns this parameter
        use_image_names: bool
            If True, the default parameters used when saving a dataset, is defined by the
            ``Images.parameter``. If Flase, the true values are defined by ``Images.image_name.parameter``.

        Returns
        =======
        disambigous_param: str
            The parameter in the mapping which value should be used if the input is ambigous.
            This can be identical to the input parameter.
        """
        if param in _AMBIGOUS_IMAGING_PARAMETERS.keys():
            if _AMBIGOUS_IMAGING_PARAMETERS[param] not in self._parset.keys():
                return param
            elif self._parset[_AMBIGOUS_IMAGING_PARAMETERS[param]] == self._parset[param]:
                return param
            else:
                if use_image_names:
                    return _AMBIGOUS_IMAGING_PARAMETERS[param]
                else:
                    return param
        
        elif param in _AMBIGOUS_IMAGING_PARAMETERS.values():
            inverse_ambigous_mapping = {v: k for k, v in _AMBIGOUS_IMAGING_PARAMETERS.items()}

            if inverse_ambigous_mapping[param] not in self._parset.keys():
                return param
            elif self._parset[inverse_ambigous_mapping[param]] == self._parset[param]:
                return param
            else:
                if use_image_names:
                    return param
                else:
                    return inverse_ambigous_mapping[param]
        else:
            return param


    def check_if_parset_sorted(self):
        """This function checks if the ._parset dictionary is sorted by  the global _MAPPING_ORDER or not.

        Parameters
        ==========

        Returns
        =======
        sorted: bool
            True, if the ._parset dictionary is sorted and False if not
        """
        last_key_val = _MAPPING_ORDER[list(self._parset.keys())[0]]
        for k in list(self._parset.keys()):
            #print(self._mapping_order[k])
            if _MAPPING_ORDER[k] < last_key_val:
                return False
            else:
                last_key_val = _MAPPING_ORDER[k]

        return True

    def sort_parset(self):
        """Sort the ._parset dictionary based on the ._mapping_oder parameter

        This is a crucial function, especially when saving parsets as this bit of code
        assures that the parset saved have the parameters in a logical order.

        Parameters
        ==========

        Returns
        =======
        :obj: `Parset`
            With updated ._parset dictionary if needed. Note that the ._parset attribute
            is deleted and re-created within this function!
        """
        if not self.check_if_parset_sorted():
            log.debug('Sort parset parameters.')

            #Create a sorted list of the mapping keys where the keys not defined int the Parset are set to None
            sorted_keys = [k if k in self._parset.keys() else None for k, v in sorted(_MAPPING_ORDER.items(), key=lambda item: item[1])]

            #Remove Nones
            sorted_keys = [k for k in sorted_keys if k != None]

            #Sorted keys and values given in a list format
            parset_buffer = sorted(self._parset.items(), key=lambda pair: sorted_keys.index(pair[0]))
            
            #Re-define ._parset where the sorting order will be determined by the order of parameters defined
            del self._parset
            object.__setattr__(self, "_parset", {})

            for item in parset_buffer:
                self._parset[item[0]] = item[1]

            del parset_buffer
        else:
            log.debug('Parset parameters are already sorted!')

    def update_parset_mapping(self, image_names=_DEFAULT_IMAGE_NAMES, gridder_name=_DEFAULT_GRIDDER_NAME):
        """Update the mapping used between the ``dstack`` and ``YandaSoft`` parset variables.
        It also updates the parameters defined. Therefore, ths function supposed to be used when
        one wants to change the attributes affecting the mapping, as this keeps everything consistent.

        Note, that the preconditioner is not updated, as all supported preconditioners are included in the
        default mapping!

        Parameters
        ==========
        image_names: str, optional
            The ``Names`` parameter of the parset. The template parset has to have this ``Names``
            parameters (if used), when read in. Nevertheless, this can be changed on the fly, and
            parsets with different names can be created. Use the ``update_parset_mapping()`` function
            for this.

        gridder_name: str, optional
            The ``gridder`` parameter of ``YandaSoft`` imager task.

        Returns
        =======
        :obj:`Parset`
            With updated mapping and associated attributes
        """
        log.info('Update Parset mapping using image_names = {0:s} and gridder = {1:s}'.format(image_names,gridder_name))
        self._image_names = image_names
        self._gridder_name = gridder_name
        pm, ipm = create_parset_mapping(image_names=self._image_names,
                                        gridder_name=self._gridder_name)
        
        #NOTE that the ordering is not updated!
        self._mapping = pm
        self._inverse_mapping = ipm

        #Also update the INames and gridder values in ._parset
        self._parset['INames'] = str([self._image_names])
        self._parset['gridder'] = str(self._gridder_name)

    def update_image_names(self, image_names=_DEFAULT_IMAGE_NAMES):
        """Update the INames parameter and also the mapping. Basically calls
        ``update_parset_mapping()`` but only update Inames.

        Parameters
        ==========
        image_names: str, optional
            The ``Names`` parameter of the parset. The template parset has to have this ``Names``
            parameters (if used), when read in. Nevertheless, this can be changed on the fly, and
            parsets with different names can be created. Use the ``update_parset_mapping()`` function
            for this.
        Returns
        =======
        :obj:`Parset`
            With updated Inames and mapping attributes
        """
        self.update_parset_mapping(image_names=image_names,gridder_name=self._gridder_name)

    def update_gridder(self, gridder_name=_DEFAULT_GRIDDER_NAME):
        """Update the gridder parameter and also the mapping. Basically calls
        ``update_parset_mapping()`` but only update the gridder.

        Parameters
        ==========
        gridder_name: str, optional
            The ``gridder`` parameter of ``YandaSoft`` imager task.
        Returns
        =======
        :obj:`Parset`
            With updated gridder and mapping attributes
        """
        self.update_parset_mapping(image_names=self._image_names,gridder_name=gridder_name)

    def update_imager(self, imager):
        """Go-to routine when updating the imager.

        Parameters
        ==========
        imager: str
            Have to be a selected ``YandaSoft`` Imager task. When a parset file is created
            this attribute is used to define the imager

        Returns
        =======
        :obj:`Parset`
            With updated imager attribute
        """
        if imager not in _SUPPORTED_IMAGERS:
            raise NameError('Imager {0:s} is not supported!'.format(imager))

        log.info('Update Parset imager to {0:s}'.format(imager))
        self._imager = imager

    def add_preconditioner(self,preconditioner):
        """Add a new preconditioner to the _preconditioner attribute

        If the given preconditioner is already used, it won't be duplicated again

        Parameters
        ==========
        preconditioner: str
            A valid (supported) preconditioner that will be added to the
            list of preconditioners inspected when saving a parset
        Returns
        =======
        :obj:`Parset`
            With an extra preconditioner in the _preconditioner attribute
        """
        if preconditioner not in _SUPPORTED_PRECONDITIONERS:
            raise NameError('Preconditioner {0:s} is not supported!'.format(preconditioner))
        if preconditioner not in self._preconditioner:
            log.info("Preconditioner '{0:s}' added to Parset preconditioners".format(preconditioner))
            self._preconditioner.append(preconditioner)

    def remove_preconditioner(self,preconditioner):
        """Remove the given preconditioner from the _preconditioner list attribute

        If the given preconditioner is not in the list nothing happens

        Parameters
        ==========
        preconditioner: str
            A valid (supported) preconditioner that will be removed from the
            list of preconditioners inspected when saving a parset
        Returns
        =======
        :obj:`Parset`
            Withouth the removed preconditioner in the _preconditioner attribute
        """
        if preconditioner not in _SUPPORTED_PRECONDITIONERS:
            raise NameError('Preconditioner {0:s} is not supported!'.format(preconditioner))
        if preconditioner in self._preconditioner:
            log.info("Preconditioner '{0:s}' removed from Parset preconditioners".format(preconditioner))
            self._preconditioner.remove(preconditioner)

    def update_preconditioner(self,preconditioners):
        """Update the _preconditioner list attribute with the
        given list of preconditioners.

        Parameters
        ==========
        preconditioners: list
            List of valid (supported) preconditioners that will be used as the new _preconditioner list
        Returns
        =======
        :obj:`Parset`
            With updated _preconditioner attribute
        """
        if preconditioners != []:
            for preconditioner in preconditioners:
                if preconditioner not in _SUPPORTED_PRECONDITIONERS:
                    raise NameError('Preconditioner {0:s} is not supported!'.format(preconditioner))

        log.info('Update preconditioner to: {0:s}'.format(str(preconditioners)))
        self._preconditioner = preconditioners

    def special_setup_for_saving_parsets(self):
        """There are some caveats  when using the ``Preconditioner`` class as it is so versatile.
        ``YandaSoft`` on the other hand have some tricky restrictions. To accommodate special cases, this
        function is used as the last step when a parset is saved to a file.

        Currently there are one special cases:
            - When WProject gridder used jointly with Wiener filtering the parameter Preservecf has to be set to \
            True, in order to compute the PCF. This is extremely important when the dumpgrid parameter is set to true, \
            as only in this case the correct PCF is dumped.

        So this function is basically secure that these special cases are met when a parset is written.

        Parameters
        ==========
 
        Returns
        =======
        :obj:`Parset`
            With updated attributes to make sure ``YandaSoft`` returns the expected results
        """
        if self._gridder_name == 'WProject' and 'Wiener' in self._preconditioner:
            if 'Preservecf' not in self._parset.keys() or self._parset['Preservecf'] == 'False':
                self.add_parset_parameter('Preservecf','True')

        return True

    def save_parset(self, output_path, parset_name, overwrite=True, use_image_names=False):
        """Save the in-memory ``Parset`` to ``output_path/parset_name``.
        The saved parset can be fed into ``YandaSoft``

        Parameters
        ==========
        output_path: str
            Full path to the folder in which the parset will be saved.

        parset_name:
            Name of the parset file created.

        overwrite: bool, optional
            If True, then the parset will be overwritten if existed.

        use_image_name: bool, optional
            The parameter with the same mname defined in ``set_image_names_param_consistency()``.
            Basicaly how to handle ambigous naming in the Images. parameters

        Returns
        ========
        Parset file: Parset file readable by ``YandaSoft``
            Create the parset file at ``output_path/parset_name``
        """
        parset_path = os.path.join(output_path, parset_name)

        if os.path.isdir(parset_path) and overwrite == False: 
            raise TypeError('Parset file already exist, and the overwrite parameters is set to False!')

        log.debug('Save Parset parameters to: {0:s}'.format(parset_path))

        #Sort the parset
        self.sort_parset()

        log.info('Save parset as: {0:s}'.format(parset_path))

        #Check some special considerations
        self.special_setup_for_saving_parsets()

        with open(parset_path, 'w') as f:
            for key in self._parset.keys():
                if check_parameter_and_Imager_compatibility(key, imager=self._imager):
                    #Check preconditioning and use the ._preconditioner attribute instead of the ._param['PNames'] attribute!
                    if key == 'PNames':
                        if self._preconditioner == []:
                            print('#{0:s}.{1:s} = {2:s}'.format(self._imager,self._mapping[key],str(self._preconditioner)),file=f)
                        else:
                            print('{0:s}.{1:s} = {2:s}'.format(self._imager,self._mapping[key],str(self._preconditioner)),file=f)

                    elif key in list(_AMBIGOUS_IMAGING_PARAMETERS.keys()) +  list(_AMBIGOUS_IMAGING_PARAMETERS.values()):
                        print('{0:s}.{1:s} = {2:s}'.format(self._imager,self._mapping[key],
                            str(self._parset[self.set_image_names_param_consistency(key,use_image_names=use_image_names)])),#Use the default imager names parameter for disambiguity
                            file=f)

                    elif check_parameter_and_Preconditioner_compatibility(key, preconditioners=self._preconditioner):
                        #We know that preconditioner and gridder settings are independent!
                        if check_parameter_and_Gridder_compatibility(key, gridder_name=self._gridder_name):
                            print('{0:s}.{1:s} = {2:s}'.format(self._imager,self._mapping[key],str(self._parset[key])),file=f)

                else:
                    continue

        #A special case, I added in order to secure the pcf output if the dumpgrid option is used
        #This is tested in the testing module!
        if self._preconditioner == [] and self._imager == 'Cimager' and 'dumpgrids' in self._parset.keys():
            log.info('The dumpgrids option is set to {0:s}, but no preconditioning is selected!'.format(str(self._parset['dumpgrids'])))
            log.info('This special case is handeled by adding preconditioner=[] and preservecf=True, which results in a pcf output!')
            with open(parset_path, 'a') as f:
                print('{0:s}.{1:s} = {2:s}'.format(self._imager,self._mapping['PNames'],str(self._preconditioner)),file=f)
                print('{0:s}.{1:s} = {2:s}'.format(self._imager,self._mapping['Preservecf'],'true'),file=f)

if __name__ == "__main__":
    pass

