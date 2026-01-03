"""
Doctors availability module for NFZ (Polish National Health Fund) API.

Provides functions to fetch and normalize medical queue data from NFZ API.
"""

from .availability import (
    get_location_from_coords,
    get_doctor_availability,
    get_doctor_coordinates,
    get_coordinates_from_address,
    PROVINCE_CODES,
)

__all__ = [
    "get_location_from_coords",
    "get_doctor_availability",
    "get_doctor_coordinates",
    "get_coordinates_from_address",
    "PROVINCE_CODES",
]
