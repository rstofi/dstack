"""Script to create publication-quality plots
for some  DINGO talk

This is a quick and dirty code focusing only onthe plots needed
"""
import os, sys
import shutil
import numpy as np
import logging
import warnings

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.offsetbox import AnchoredText
from matplotlib.patheffects import withStroke
 
import dstack as ds

#Import fancy triangle plots from svalidation
import svalidation

#=== Globals ===
#RCparams for plotting
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'

matplotlib.rcParams['xtick.major.size'] = 9
matplotlib.rcParams['ytick.major.size'] = 9

matplotlib.rcParams['xtick.major.width'] = 3
matplotlib.rcParams['ytick.major.width'] = 3

matplotlib.rcParams['axes.linewidth'] = 2

plt.rcParams['xtick.labelsize']=16
plt.rcParams['ytick.labelsize']=16

#4 sampled colors from viridis
c0 = '#440154';#Purple
c1 = '#30678D';#Blue
c2 = '#35B778';#Greenish
c3 = '#FDE724';#Yellow

outlier_color = 'dimgrey'

#=== Setup logging ===
log = logging.getLogger(__name__)

#=== MAIN ===

#Decide what to plot
nice_contour_plots = True
singe_flux_plot = False
spectra_triangle_plot = False
moment_map_triangle_plots = False
diff_scaling_plots = False
high_res_moment_maps = False
high_resolution_spectra = False
moment_maps_for_daily_minor_vs_major_cycles = False

#=== Contour plots
if nice_contour_plots:
    #Setup the parameters of the galaxy imaged
    working_dir = '/home/krozgonyi/Desktop/quick_and_dirty_sofia_outputs/'
    
    source_ID = 1
    sofia_dir_path = working_dir + 'stacked_grids/'
    name_base = 'beam17_all_'
    output_name = working_dir + 'slide_figures/moment_contours_NGC7361.pdf'
    spectra_output_name = working_dir + 'slide_figures/spectra_NGC7361.pdf'
    
    b_maj = 30.
    b_min = 30.
    b_pa = 0.
    
    central_vel = 1246 #central velocity in mom1 map
    delta_vel = 20.
    
    mom0_contour_levels = [0.5, 1.6, 2.7, 5.3, 13]
    mom1_contour_levels = [i * delta_vel + central_vel for i in range(-8,7)]
    
    #Get the optical background image
    N_optical_pixels = 750
    optical_im, optical_im_wcs, survey_used = ds.sdiagnostics.get_optical_image_ndarray(
            source_ID, sofia_dir_path, name_base, N_optical_pixels=N_optical_pixels)
        
    #Get the moment maps
    
    col_den_map, mom0_wcs, col_den_sen_lim = ds.sdiagnostics.get_momN_ndarray(0,
            source_ID, sofia_dir_path, name_base, b_maj=b_maj, b_min=b_min,
            masking=False, mask_sigma=1.) #So we can draw the contours of the low column density regions
    
    mom1_map, mom1_wcs, col_den_sen_lim = ds.sdiagnostics.get_momN_ndarray(1,
            source_ID, sofia_dir_path, name_base, b_maj=b_maj, b_min=b_min,
            masking=True, mask_sigma=3.5) #So we can draw the contours of the low column density regions
    
    
    #Print contour levels
    #print(col_den_sen_lim)
    #for cl in mom0_contour_levels:
    #    print('The {0:f} sigma contour equivalent to  {1:f} col density'.format(
    #        cl, cl*col_den_sen_lim))
    
    #Create the plot
    fig, axes = plt.subplots(figsize=(12, 7),
                    sharex=True, sharey=True, ncols=2, nrows=1,
                    subplot_kw={'projection': optical_im_wcs})
    
    #First plot
    axes[0].imshow(optical_im, origin='lower', cmap='Greys')
                    
    axes[0].contour(col_den_map, levels=np.array(mom0_contour_levels),
            transform=axes[0].get_transform(mom0_wcs),
            colors=c2, linewidths=1.5, alpha=1.)
    
    #Second plot
    axes[1].imshow(optical_im, origin='lower', cmap='Greys')
                    
    axes[1].contour(mom1_map, levels=mom1_contour_levels,
            transform=axes[1].get_transform(mom1_wcs),
            colors=c2, linewidths=1.5, alpha=1.)
    
    #Add beam ellipse
    beam_loc_ra = optical_im_wcs.array_index_to_world(int(0.1 * N_optical_pixels),
            int(0.1 * N_optical_pixels)).ra.value
    beam_loc_dec = optical_im_wcs.array_index_to_world(int(0.1 * N_optical_pixels),
            int(0.1 * N_optical_pixels)).dec.value
    
    
    beam_ellip = Ellipse((beam_loc_ra, beam_loc_dec), b_maj/3600, b_min/3600, b_pa,
            lw=1.5, fc=outlier_color, ec='black', alpha=1., transform=axes[0].get_transform('fk5'))
    
    axes[0].add_patch(beam_ellip)
    
    #Need to do this for matplotlib
    beam_ellip = Ellipse((beam_loc_ra, beam_loc_dec), b_maj/3600, b_min/3600, b_pa,
            lw=1.5, fc=outlier_color, ec='black', alpha=1., transform=axes[1].get_transform('fk5'))
    
    axes[1].add_patch(beam_ellip)
    
    #Add text
    t = ds.sdiagnostics.add_inner_title(axes[0], 'Total HI', loc=2, 
                                prop=dict(size=24,color='black'),
                                white_border=False)
    
    t.patch.set_ec("none")
    t.patch.set_alpha(1.)
    
    t = ds.sdiagnostics.add_inner_title(axes[1], 'Velocity HI', loc=2, 
                                prop=dict(size=24,color='black'),
                                white_border=False)
    
    t.patch.set_ec("none")
    t.patch.set_alpha(1.)
    
    #Set labels
    axes[1].coords[1].set_ticklabel_visible(False)
    
    #Dec lable
    axes[0].coords[1].set_axislabel('Declination (J2000)', fontsize=20)
    
    
    #Add a subplot in the background with nothing in it and invisible axes, and use
    # its axes for the shared labels => only for x axis
    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axis
    plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
    plt.xlabel('Right Ascension (J2000)', fontsize=20, labelpad=-10)
    #plt.ylabel('Declination (J2000)', fontsize=18)
    
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.05, hspace=0.)
    
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
    
    #exit()


if singe_flux_plot:
    #=== Flux
    #Get the flux arrays.
    flux, velocity = ds.sdiagnostics.get_spectra_array(source_ID, sofia_dir_path, name_base, 
            v_frame='optical', beam_correction=True,
            b_maj_px=5., b_min_px=5.)
    
    #Create the plot
    mm2in = lambda x: x*0.03937008
    
    #Set the fig size to match so I can add it to the LaTeX document nicely
    
    #width = mm2in(0.35/0.6*263)
    #height = (145/263) * width
    
    #print(width,height)
    
    fig = plt.figure(1, figsize=(6,7))
    ax = fig.add_subplot(111)
    
    ax.step(velocity, flux, lw=2.5, c=c2)
    
    #Set labels and lims
    #ax.set_xlim((22300,23050))
    
    
    ax.tick_params(axis='both', which='major', labelsize=17)
    
    ax.set_xlabel(r'Velocity (km s$^{-1}$)', fontsize=20, labelpad=10)
    ax.set_ylabel('Flux density (mJy)', fontsize=20)
    #ax.grid()
    
    #Add inner title
    t = ds.sdiagnostics.add_inner_title(ax, 'Spectra', loc=1, prop=dict(size=25, color='black'),
                white_border=False)
    
    t.patch.set_ec("none")
    t.patch.set_alpha(0.5)
    
    
    plt.gcf().set_size_inches(mm2in(282/2),mm2in(154))
    
    plt.savefig(spectra_output_name,bbox_inches='tight')
    plt.close()

if spectra_triangle_plot:
    #=== Fancy triangle plots
    #Spectra
    working_dir = '/home/krozgonyi/Desktop/quick_and_dirty_sofia_outputs/'
    
    sofia_dir_path_list = list(map(working_dir.__add__,['co_added_visibilities/',
        'stacked_grids/', 'stacked_images/']))
    
    log.info('Creating spectra triangle plot for 2km baselie results...')
    
    
    svalidation.plot_spectra_triangle_matrix(source_ID_list = [1, 1, 1],
            sofia_dir_list = sofia_dir_path_list,
            name_base_list = ['beam17_all_'],
            output_name = working_dir + 'slide_figures/spectras.pdf',
            beam_correction_list = [True, True, True],
            b_maj_px_list = [5.0],
            b_min_px_list = [5.0],
            color_list = [c0, c2, c1],
            label_list = ['co-added visibilities', 'stacked grids', 'stacked images'],
            ident_list = ['V', 'G', 'I'])
    
    log.info('...done')
    
    #exit()
     
if moment_map_triangle_plots:
    #Moment maps
    working_dir = '/home/krozgonyi/Desktop/quick_and_dirty_sofia_outputs/'
     
    sofia_dir_path_list = list(map(working_dir.__add__,['co_added_visibilities/',
        'stacked_grids/', 'stacked_images/']))
     
     
    for mom in range(0,3):
        log.info('Creating mom{0:d} contour triangle plot for 2km baselie results...'.format(mom))
     
     
        svalidation.plot_momN_triangle_matrix(moment = mom,
                source_ID_list=[1, 1, 1],
                sofia_dir_list = sofia_dir_path_list,
                name_base_list = ['beam17_all_'],
                output_name = working_dir + 'slide_figures/mom{0:d}_map.pdf'.format(mom),
                N_optical_pixels = 170,
                masking_list = [True],
                mask_sigma_list = [3.5],
                color_list = [c0, c2, c1],
                label_list = ['co-added visibilities', 'stacked grids', 'stacked images'],
                ident_list = ['V', 'G', 'I'],
                b_maj_list = [30, 30, 30],
                b_min_list = [30, 30, 30],
                b_pa_list = [0, 0, 0])
     
        
        log.info('..done')
     
     
        #Also create the sensitivity map
        if mom == 0:
            log.info('Creating the sensitivity triangle plot...')
     
     
            #Use the column densizty sensitivity of the co-added visibility combination
            # for all the sensitivity maps
            mmap, mmap_wcs, sen_lim = ds.sdiagnostics.get_momN_ndarray(moment = 0,
                source_ID = 1,
                sofia_dir_path = sofia_dir_path_list[0],
                name_base = 'beam17_all_',
                b_maj = 30,
                b_min = 30)
     
     
            svalidation.plot_momN_triangle_matrix(moment = mom,
                source_ID_list=[1, 1, 1],
                sofia_dir_list = sofia_dir_path_list,
                name_base_list = ['beam17_all_'],
                output_name = working_dir + 'slide_figures/sensitivity_map.pdf'.format(mom),
                N_optical_pixels = 170,
                masking_list = [True],
                mask_sigma_list = [3.5],
                color_list = [c0, c2, c1],
                label_list = ['co-added visibilities', 'stacked grids', 'stacked images'],
                ident_list = ['V', 'G', 'I'],
                b_maj_list = [30, 30, 30],
                b_min_list = [30, 30, 30],
                b_pa_list = [0, 0, 0],
                col_den_sensitivity_lim_list = [sen_lim, sen_lim, sen_lim],
                sensitivity = True)
        
            log.info('...done')
     
            #exit()
     
if diff_scaling_plots:
    #2km baselines
    working_dir = '/home/krozgonyi/Desktop/quick_and_dirty_sofia_outputs/'
    
    sofia_dir_path_list = list(map(working_dir.__add__,['co_added_visibilities/',
        'stacked_grids/', 'stacked_images/']))
    
    #Use the column densizty sensitivity of the co-added visibility combination
    # for all the sensitivity maps
    mmap, mmap_wcs, sen_lim = ds.sdiagnostics.get_momN_ndarray(moment = 0,
        source_ID = 1,
        sofia_dir_path = sofia_dir_path_list[0],
        name_base = 'beam17_all_',
        b_maj = 30,
        b_min = 30)
    
    
    ID_list = [1, 1, 1]
    ident_list = ['V', 'G', 'I']
    
    for i in range(0,3):
        for j in range(0,3):
            if j>i:
                diff_ident = '({0:s} - {1:s})'.format(ident_list[i],
                        ident_list[j])
    
                log.info('Creating sensitivity diff against column density plots for {}...'.format(
                    diff_ident))
    
                for zoom_name, col_den_binwidth, col_den_lim in zip(['high', 'low'], [19., 6.5], [None, (3.5, 100)]):
                    svalidation.plot_flux_density_diff_dependience_on_column_density(source_ID_list=[ID_list[i],ID_list[j]],
                        sofia_dir_list = [sofia_dir_path_list[i], sofia_dir_path_list[j]],
                        name_base_list = ['beam17_all_'],
                        output_fname = working_dir + 'slide_figures/sensitivity_column_density_{0:s}_{1:s}{2:s}_map.pdf'.format(
                            zoom_name, ident_list[i], ident_list[j]),
                        N_optical_pixels = 170,
                        masking_list = [True],
                        mask_sigma_list = [3.5],
                        b_maj_list = [30, 30],
                        b_min_list = [30, 30],
                        b_pa_list = [0, 0],
                        ident_string = diff_ident,
                        col_den_sensitivity_lim_list = [sen_lim],
                        beam_correction = True,
                        b_maj_px_list = [5.],
                        b_min_px_list = [5.],
                        col_den_binwidth = col_den_binwidth,
                        diff_binwidth = 0.005,
                        col_den_lim = col_den_lim,
                        sensitivity=True,
                        logbins=True)    
        
                log.info('..done')
    

if high_res_moment_maps:

    #6km baselines
    working_dir = '/home/krozgonyi/Desktop/quick_and_dirty_sofia_outputs/high_resolution/'

    sofia_dir_path_list = list(map(working_dir.__add__,['co_added_visibilities/',
        'stacked_grids/', 'stacked_images/']))


    for mom in range(0,3):
        log.info('Creating mom{0:d} contour triangle plot for 6km baselie results...'.format(mom))

        svalidation.plot_momN_triangle_matrix(moment = mom,
                source_ID_list=[1, 1, 1],
                sofia_dir_list = sofia_dir_path_list,
                name_base_list = ['beam17_all_'],
                output_name = working_dir + 'slide_figures/high_res_mom{0:d}_map.pdf'.format(mom),
                N_optical_pixels = 400,
                masking_list = [True],
                mask_sigma_list = [3.5],
                color_list = [c0, c2, c1],
                label_list = ['co-added visibilities', 'stacked grids', 'stacked images'],
                ident_list = ['V', 'G', 'I'],
                b_maj_list = [12, 12, 12],
                b_min_list = [12, 12, 12],
                b_pa_list = [0, 0, 0])

        log.info('..done')
        
        #Also create the sensitivity map
        if mom == 0:
            log.info('Creating the sensitivity triangle plot...')


            #Use the column densizty sensitivity of the co-added visibility combination
            # for all the sensitivity maps
            mmap, mmap_wcs, sen_lim = ds.sdiagnostics.get_momN_ndarray(moment = 0,
                source_ID = 1,
                sofia_dir_path = sofia_dir_path_list[0],
                name_base = 'beam17_all_',
                b_maj = 12,
                b_min = 12)


            svalidation.plot_momN_triangle_matrix(moment = mom,
                source_ID_list=[1, 1, 1],
                sofia_dir_list = sofia_dir_path_list,
                name_base_list = ['beam17_all_'],
                output_name = working_dir + 'slide_figures/high_res_sensitivity_map.pdf'.format(mom),
                N_optical_pixels = 400,
                masking_list = [True],
                mask_sigma_list = [3.0],
                color_list = [c0, c2, c1, outlier_color],
                label_list = ['co-added visibilities', 'stacked grids', 'stacked images'],
                ident_list = ['V', 'G', 'I'],
                b_maj_list = [12, 12, 12],
                b_min_list = [12, 12, 12],
                b_pa_list = [0, 0, 0],
                col_den_sensitivity_lim_list = [sen_lim],
                sensitivity = True)
        
            log.info('...done')

if high_resolution_spectra:
    #6km baselines
    working_dir = '/home/krozgonyi/Desktop/quick_and_dirty_sofia_outputs/high_resolution/'

    sofia_dir_path_list = list(map(working_dir.__add__,['co_added_visibilities/',
        'stacked_grids/', 'stacked_images/']))

    log.info('Creating spectra triangle plot for 6km baselie results...')

    svalidation.plot_spectra_triangle_matrix(source_ID_list = [1, 1, 1],
            sofia_dir_list = sofia_dir_path_list,
            name_base_list = ['beam17_all_'],
            output_name = working_dir + 'slide_figures/high_res_spectras.pdf',
            beam_correction_list = [True, True, True],
            b_maj_px_list = [6.0],
            b_min_px_list = [6.0],
            color_list = [c0, c2, c1],
            label_list = ['co-added visibilities', 'stacked grids', 'stacked images'],
            ident_list = ['V', 'G', 'I'])

    log.info('...done')

    exit()

if moment_maps_for_daily_minor_vs_major_cycles:
    #Moment maps
    working_dir = '/home/krozgonyi/Desktop/quick_and_dirty_sofia_outputs/'
     
    sofia_dir_path_list = list(map(working_dir.__add__,['co_added_visibilities/',
        'stacked_grids/', 'stacked_images/', 'conventional_imaging/']))
     
     
    for mom in range(0,3):
        log.info('Creating mom{0:d} contour triangle plot for 2km baselie results...'.format(mom))
     
     
        svalidation.plot_momN_triangle_matrix(moment = mom,
                source_ID_list=[1, 1, 1, 2],
                sofia_dir_list = sofia_dir_path_list,
                name_base_list = ['beam17_all_'],
                output_name = working_dir + 'slide_figures/deconvolution_dependence_mom{0:d}_map.pdf'.format(mom),
                N_optical_pixels = 170,
                masking_list = [True],
                mask_sigma_list = [3.5],
                color_list = [c0, c2, c1, outlier_color],
                label_list = ['co-added visibilities', 'stacked grids', 'stacked images', 'conventional imaging'],
                ident_list = ['G', 'I', 'C'],
                b_maj_list = [30, 30, 30],
                b_min_list = [30, 30, 30],
                b_pa_list = [0, 0, 0])
     
        
        log.info('..done')
     
