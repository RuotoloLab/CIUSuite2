"""
Dan Polasky
10/6/17
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import numpy as np


class CIUAnalysisObj(object):
    """
    Container for analysis/processed information from a CIU fingerprint. Requires a CIURaw object
    to start, additional fields added as data is processed.
    """
    def __init__(self, ciu_raw_obj, ciu_data, axes, gauss_params=None):
        """
        Initialize with raw data and axes. Allows addition of Gaussian fitting data later
        :param ciu_raw_obj: Object containing initial raw data, axes, and filepath of the analysis
        :param ciu_data: pre-processed data (smoothed/interpolated/cropped/etc) - can be modified repeatedly
        :param axes: modified axes corresponding to ciu_data (axes[0] = DT, axes[1] = CV)
        :param gauss_params: List of lists of parameters for gaussians fitted to each CV (column of ciu_data)
        params are [baseline height, amplitude, centroid, width]
        """
        self.raw_obj = ciu_raw_obj
        self.ciu_data = ciu_data
        self.axes = axes

        # Gaussian fitting parameters - not always initialized with the object
        self.gauss_params = None
        self.gauss_baselines = None
        self.gauss_amplitudes = None
        self.gauss_centroids = None
        self.gauss_widths = None
        self.gauss_fwhms = None
        self.gauss_adj_r2s = None
        self.gauss_fits = None
        self.gauss_covariances = None
        self.gauss_r2s = None
        self.gauss_resolutions = None
        self.gauss_fit_stats = None
        if gauss_params is not None:
            # initialize param lists if parameters are provided
            self.init_gauss_lists(gauss_params)

    def init_gauss_lists(self, gauss_params):
        """
        Initialize human readable lists of gaussian parameters
        :param gauss_params: list of lists of gaussian parameters for each column of ciu array (each CV)
        :return: void
        """
        self.gauss_params = gauss_params
        self.gauss_baselines = [x[0] for x in gauss_params]
        self.gauss_amplitudes = [x[1] for x in gauss_params]
        self.gauss_centroids = [x[2] for x in gauss_params]
        self.gauss_widths = [x[3] for x in gauss_params]

    def save_gaussfits_pdf(self, outputpath):
        """
        Save a pdf containing an image of the data and gaussian fit for each column to pdf in outputpath.
        :param outputpath: directory in which to save output
        :return: void
        """
        # ensure gaussian data has been initialized
        if self.gauss_fits is None:
            print('No gaussian fit data in this object yet, returning')
            return

        print('Saving Gausfitdata_' + str(self.raw_obj.filename) + '_.pdf .....')
        pdf_fig = PdfPages(os.path.join(outputpath, 'Gausfitdata_' + str(self.raw_obj.filename) + '_.pdf'))
        intarray = np.swapaxes(self.ciu_data, 0, 1)
        for k in range(len(self.axes[1])):
            plt.figure()
            plt.scatter(self.axes[0], intarray[k])
            plt.plot(self.axes[0], self.gauss_fits[k], ls='--', color='black')
            plt.title(self.axes[1][k])
            pdf_fig.savefig()
            plt.close()
        pdf_fig.close()
        print('Saving Gausfitdata_' + str(self.raw_obj.filename) + '_.pdf DONE')

    def plot_centroids(self, outputpath):
        """
        Save a png image of the centroid DTs fit by gaussians
        :param outputpath: directory in which to save output
        :return: void
        """
        print('Saving TrapCVvsArrivtimecentroid ' + str(self.raw_obj.filename) + '_.png .....')
        plt.scatter(self.axes[1], self.gauss_centroids)
        plt.xlabel('Trap CV')
        plt.ylabel('ATD_centroid')
        plt.grid('on')
        plt.savefig(os.path.join(outputpath, 'TrapCVvsArrivtimecentroid_' + str(self.raw_obj.filename) + '_.png'),
                    dpi=500)
        plt.close()
        print('Saving TrapCVvsArrivtimecentroid ' + str(self.raw_obj.filename) + '_.png DONE')

    def plot_fwhms(self, outputpath):
        """
        Save a png image of the FWHM (widths) fit by gaussians
        :param outputpath: directory in which to save output
        :return: void
        """
        print('Saving TrapcCVvsFWHM_' + str(self.raw_obj.filename) + '_.png .....')
        plt.scatter(self.axes[1], self.gauss_fwhms)
        plt.xlabel('Trap CV')
        plt.ylabel('ATD_FWHM')
        plt.grid('on')
        plt.savefig(os.path.join(outputpath, 'TrapCVvsFWHM_' + str(self.raw_obj.filename) + '_.png'), dpi=500)
        plt.close()
        print('Saving TrapcCVvsFWHM_' + str(self.raw_obj.filename) + '_.png DONE')

    def save_gauss_params(self, outputpath):
        """
        Save all gaussian information to file
        :param outputpath: directory in which to save output
        :return: void
        """
        outarray = [self.axes[0], self.gauss_centroids, self.gauss_widths, self.gauss_fwhms,
                    self.gauss_resolutions, self.gauss_r2s, self.gauss_adj_r2s]
        outarray = np.array(outarray[0], dtype='float')
        outarray2 = np.transpose(outarray)

        print('Saving files ...')
        np.save(os.path.join(outputpath, str(self.raw_obj.filename) + '_curvefit_popt.npy'), self.gauss_params)
        print(str(self.raw_obj.filename) + '_curvefit_popt.npy')
        np.save(os.path.join(outputpath, str(self.raw_obj.filename) + '_curvefit_pcov.npy'), self.gauss_covariances)
        print(str(self.raw_obj.filename) + '_curvefit_pcov.npy')
        np.save(os.path.join(outputpath, str(self.raw_obj.filename) + '_curvefit_stats.npy'), self.gauss_fit_stats)
        print(str(self.raw_obj.filename) + '_curvefit_stats.npy')
        np.savetxt(os.path.join(outputpath, str(self.raw_obj.filename) + '_outarraygaussfit.csv'), outarray2,
                   delimiter=',', fmt='%s',
                   header='TrapCV, ATD_centroid, ATD_width, ATD_FWHM, ATD_Resolution, R^2, Adj_R^2')
