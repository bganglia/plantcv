# Read in a hyperspectral data cube as an array and parse metadata from the header file

import os
import cv2
import numpy as np
from plantcv.plantcv import params
from plantcv.plantcv import plot_image
from plantcv.plantcv import print_image


def _find_closest(A, target):
    #A must be sorted
    idx = A.searchsorted(target)
    idx = np.clip(idx, 1, len(A)-1)
    left = A[idx-1]
    right = A[idx]
    idx -= target - left < right - target
    return idx

def read_data(filename):
    """Read hyperspectral image data from file.

        Inputs:
        filename = name of image file

        Returns:
        raw_data    = image object as numpy array
        bands       = number of bands
        wavelengths = list of wavelengths

        :param filename: str
        :param mode: str
        :return img: numpy.ndarray
        :return bands: ing
        :return wavelengths: list
        """
    # Initialize dictionary
    header_dict = {}

    raw_data = np.fromfile(filename, np.float32, -1)

    headername = filename + ".hdr"

    with open(headername, "r") as f:
        # Replace characters for easier parsing
        hdata = f.read()
        hdata = hdata.replace("\n,", ",")
        hdata = hdata.replace("{\n", "{")
        hdata = hdata.replace("\n}", "}")
        hdata = hdata.replace(";", "")
    hdata = hdata.split("\n")
    # Loop through and create a dictionary from the header file
    for i, string in enumerate(hdata):
        if '=' in string:
            header_data = hdata[i].split(" = ")
            header_dict.update({header_data[0]: header_data[1].rstrip()})
        elif ':' in string:
            header_data = header_data[i].split(" : ")
            header_dict.update({header_data[0] : header_data[1].rstrip()})

    # Reshape the raw data into a datacube array
    array_data = raw_data.reshape(int(header_dict["lines"]),
                                  int(header_dict["bands"]),
                                  int(header_dict["samples"])).transpose((0, 2, 1))

    # Reformat wavelengths
    header_dict["wavelength"] = header_dict["wavelength"].replace("{", "")
    header_dict["wavelength"] = header_dict["wavelength"].replace("}", "")
    header_dict["wavelength"] = header_dict["wavelength"].split(",")

    if "default bands" in header_dict:
        header_dict["default bands"] = header_dict["default bands"].replace("{", "")
        header_dict["default bands"] = header_dict["default bands"].replace("}", "")
        default_bands = header_dict["default bands"].split(",")

        pseudo_rgb = cv2.merge((array_data[:, :, int(default_bands[0])],
                                array_data[:, :, int(default_bands[1])],
                                array_data[:, :, int(default_bands[2])]))
    else:
        wavelength_dict = {}
        for j, wavelength in enumerate(header_dict["wavelength"]):
            wavelength_dict.update({wavelength: j})

        max_wavelength = max([float(i) for i in wavelength_dict.keys()])
        min_wavelength = min([float(i) for i in wavelength_dict.keys()])

        # Check range of available wavelength
        if max_wavelength >= 635 and min_wavelength <= 490:
            id_red = _find_closest(np.array([float(i) for i in wavelength_dict.keys()]), 635)
            id_green = _find_closest(np.array([float(i) for i in wavelength_dict.keys()]), 520)
            id_blue = _find_closest(np.array([float(i) for i in wavelength_dict.keys()]), 450)

            pseudo_rgb = cv2.merge((array_data[:, :, [id_red]],
                                    array_data[:, :, [id_green]],
                                    array_data[:, :, [id_blue]]))
    #  add method when there isn't suggested rgb values

    if params.debug == "plot":
        plot_image(pseudo_rgb)
    elif params.debug == "print":
        print_image(pseudo_rgb, os.path.join(params.debug_outdir, str(params.device) + "_pseudo_rgb.png"))

    return array_data, header_dict
