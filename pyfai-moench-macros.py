from sardana.macroserver.macro import imacro, macro, Type, Optional
from tango import DeviceProxy
import numpy as np


@imacro(
    [
        ["energy", Type.Float, Optional, "photon energy in eV"],
        ["dist", Type.Float, Optional, "distance sample <-> detector in m"],
        ["pixel1", Type.Float, Optional, "pixel size 1 in m"],
        ["pixel2", Type.Float, Optional, "pixel size 2 in m"],
        ["npt_q", Type.Integer, Optional, "number of q bins"],
        ["npt_chi", Type.Integer, Optional, "number of chi bins"],
        ["poni2", Type.Float, Optional, "x coordinate of center in px"],
        ["poni1", Type.Float, Optional, "y coordinate of center in px"],
    ]
)
def pyfai_config_moench(
    self, energy, dist, pixel1, pixel2, npt_q, npt_chi, poni2, poni1
):
    # dict of arguments
    attr_list = [
        "wavelength",
        "energy",
        "dist",
        "poni1",
        "poni2",
        "pixel1",
        "pixel2",
        "npt_q",
        "npt_chi",
        "rot1",
        "rot2",
        "rot3",
    ]
    # there are controller for pumped and unpumped values
    # the settings will be set equally for the unpumped and pumped controller
    unpumped_controller_name = "FAI_moench_threshold"
    pumped_controller_name = "FAI_moench_threshold_pumped"

    unpumped_controller = self.getController(unpumped_controller_name)
    pumped_controller = self.getController(pumped_controller_name)

    # loading unpumped values
    default_values = {}
    for attr in attr_list:
        default_values[attr] = getattr(unpumped_controller, attr)

    # new values dict
    new_values = {}
    energy = self.input(
        "Photon energy [eV]:",
        data_type=Type.Float,
        title="photon energy",
        unit="eV",
        default_value=default_values["energy"],
    )

    # calculating wavelength based on energy
    wavelength = 1e-9
    if energy != 0:
        hc = 1.24e-6  # in eV
        wavelength = hc / energy

    new_values["energy"] = energy
    new_values["wavelength"] = wavelength

    new_values["dist"] = self.input(
        "Sample-detector distance [m]:",
        data_type=Type.Float,
        title="distance",
        default_value=default_values["dist"],
    )

    new_values["pixel1"] = self.input(
        "Pixel 1 size [m]:",
        data_type=Type.Float,
        title="pixel1 size",
        default_value=default_values["pixel1"],
    )
    new_values["pixel2"] = self.input(
        "Pixel 2 size [m]:",
        data_type=Type.Float,
        title="pixel2 size",
        default_value=default_values["pixel2"],
    )
    new_values["npt_q"] = self.input(
        "q bins amount:",
        data_type=Type.Integer,
        title="amount q of bins",
        default_value=default_values["npt_q"],
    )
    new_values["npt_chi"] = self.input(
        "chi bins amount:",
        data_type=Type.Integer,
        title="amount chi of bins",
        default_value=default_values["npt_chi"],
    )
    new_values["poni2"] = self.input(
        "x center coordinate [px]:",
        data_type=Type.Float,
        title="x coordinate in px",
        default_value=default_values["poni2"] / default_values["pixel2"],
    )
    new_values["poni1"] = self.input(
        "y center coordinate [px]:",
        data_type=Type.Float,
        title="y coordinate in px",
        default_value=default_values["poni1"] / default_values["pixel1"],
    )

    new_values["poni2"] = new_values["poni2"] * new_values["pixel2"]
    new_values["poni1"] = new_values["poni1"] * new_values["pixel1"]

    for key, value in new_values.items():
        unpumped_controller.write_attribute(key, value)
        pumped_controller.write_attribute(key, value)
