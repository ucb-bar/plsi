#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  A collection of pre-implemented LibraryFilters.
#
#  Copyright 2017-2018 Edward Wang <edward.c.wang@compdigitec.com>

import os
import warnings
from typing import TYPE_CHECKING, Any, Callable, List

from library_filter import LibraryFilter

if TYPE_CHECKING:
    # grumble grumble, we need a better Library class generator
    from library_filter import Library


class LibraryFilterHolder:
    """
    Dummy class to hold the list of properties.
    Instantiated by hammer_tech to be exposed as hammer_tech.filters.lef_filter etc.
    """

    @staticmethod
    def create_nonempty_check(description: str) -> Callable[[List[str]], List[str]]:
        """
        Create a function that checks that the list it is given has >1 element.
        :param description: Description to show in the error message.
        :return: Function that takes in the list of elements and returns a checked/processed version of itself.
        """
        def check_nonempty(l: List[str]) -> List[str]:
            if len(l) == 0:
                raise ValueError("Must have at least one " + description)
            else:
                return l

        return check_nonempty

    @property
    def timing_db_filter(self) -> LibraryFilter:
        """
        Selecting Synopsys timing libraries (.db). Prefers CCS if available; picks NLDM as a fallback.
        """

        def extraction_func(lib: "Library") -> List[str]:
            # Choose ccs if available, if not, nldm.
            if lib.ccs_library_file is not None:
                return [lib.ccs_library_file]
            elif lib.nldm_library_file is not None:
                return [lib.nldm_library_file]
            else:
                return []

        return LibraryFilter.new("timing_db", "CCS/NLDM timing lib (Synopsys .db)", extraction_func=extraction_func,
                                 is_file=True)

    @property
    def liberty_lib_filter(self) -> LibraryFilter:
        """
        Select ASCII liberty (.lib) timing libraries. Prefers CCS if available; picks NLDM as a fallback.
        """
        warnings.warn("Use timing_lib_filter instead", DeprecationWarning, stacklevel=2)

        def extraction_func(lib: "Library") -> List[str]:
            # Choose ccs if available, if not, nldm.
            if lib.ccs_liberty_file is not None:
                return [lib.ccs_liberty_file]
            elif lib.nldm_liberty_file is not None:
                return [lib.nldm_liberty_file]
            else:
                return []

        return LibraryFilter.new("timing_lib", "CCS/NLDM timing lib (ASCII .lib)",
                                 extraction_func=extraction_func, is_file=True)

    @property
    def timing_lib_filter(self) -> LibraryFilter:
        """
        Select ASCII .lib timing libraries. Prefers CCS if available; picks NLDM as a fallback.
        """

        def extraction_func(lib: "Library") -> List[str]:
            # Choose ccs if available, if not, nldm.
            if lib.ccs_liberty_file is not None:
                return [lib.ccs_liberty_file]
            elif lib.nldm_liberty_file is not None:
                return [lib.nldm_liberty_file]
            else:
                return []

        return LibraryFilter.new("timing_lib", "CCS/NLDM timing lib (ASCII .lib)",
                                 extraction_func=extraction_func, is_file=True)

    @property
    def timing_lib_with_ecsm_filter(self) -> LibraryFilter:
        """
        Select ASCII .lib timing libraries. Prefers ECSM, then CCS, then NLDM if multiple are present for
        a single given .lib.
        """

        def extraction_func(lib: "Library") -> List[str]:
            if lib.ecsm_liberty_file is not None:
                return [lib.ecsm_liberty_file]
            elif lib.ccs_liberty_file is not None:
                return [lib.ccs_liberty_file]
            elif lib.nldm_liberty_file is not None:
                return [lib.nldm_liberty_file]
            else:
                return []

        return LibraryFilter.new("timing_lib_with_ecsm", "ECSM/CCS/NLDM timing lib (liberty ASCII .lib)",
                                 extraction_func=extraction_func, is_file=True)

    @property
    def qrc_tech_filter(self) -> LibraryFilter:
        """
        Selecting qrc RC Corner tech (qrcTech) files.
        """

        def extraction_func(lib: "Library") -> List[str]:
            if lib.qrc_techfile is not None:
                return [lib.qrc_techfile]
            else:
                return []

        return LibraryFilter.new("qrc", "qrc RC corner tech file",
                                 extraction_func=extraction_func, is_file=True)

    @property
    def verilog_synth_filter(self) -> LibraryFilter:
        """
        Selecting verilog_synth files which are synthesizable wrappers (e.g. for SRAM) which are needed in some
        technologies.
        """

        def extraction_func(lib: "Library") -> List[str]:
            if lib.verilog_synth is not None:
                return [lib.verilog_synth]
            else:
                return []

        return LibraryFilter.new("verilog_synth", "Synthesizable Verilog wrappers",
                                 extraction_func=extraction_func, is_file=True)

    @property
    def lef_filter(self) -> LibraryFilter:
        """
        Select LEF files for physical layout.
        """

        def filter_func(lib: "Library") -> bool:
            return lib.lef_file is not None

        def extraction_func(lib: "Library") -> List[str]:
            assert lib.lef_file is not None
            return [lib.lef_file]

        def sort_func(lib: "Library"):
            if lib.provides is not None:
                for provided in lib.provides:
                    if provided.lib_type is not None and provided.lib_type == "technology":
                        return 0  # put the technology LEF in front
            return 100  # put it behind

        return LibraryFilter.new("lef", "LEF physical design layout library", is_file=True, filter_func=filter_func,
                                 extraction_func=extraction_func, sort_func=sort_func)

    @property
    def gds_filter(self) -> LibraryFilter:
        """
        Select GDS files for opaque physical information.
        """

        def filter_func(lib: "Library") -> bool:
            return lib.gds_file is not None

        def extraction_func(lib: "Library") -> List[str]:
            assert lib.gds_file is not None
            return [lib.gds_file]

        return LibraryFilter.new("gds", "GDS opaque physical design layout", is_file=True, filter_func=filter_func,
                                 extraction_func=extraction_func)

    @property
    def spice_filter(self) -> LibraryFilter:
        """
        Select SPICE files.
        """

        def filter_func(lib: "Library") -> bool:
            return lib.spice_file is not None

        def extraction_func(lib: "Library") -> List[str]:
            assert lib.spice_file is not None
            return [lib.spice_file]

        return LibraryFilter.new("spice", "SPICE files", is_file=True, filter_func=filter_func,
                                 extraction_func=extraction_func)

    @property
    def milkyway_lib_dir_filter(self) -> LibraryFilter:
        def select_milkyway_lib(lib: "Library") -> List[str]:
            if lib.milkyway_lib_in_dir is not None:
                return [os.path.dirname(lib.milkyway_lib_in_dir)]
            else:
                return []

        return LibraryFilter.new("milkyway_dir", "Milkyway lib", is_file=False, extraction_func=select_milkyway_lib)

    @property
    def milkyway_techfile_filter(self) -> LibraryFilter:
        """Select milkyway techfiles."""

        def select_milkyway_tfs(lib: "Library") -> List[str]:
            if lib.milkyway_techfile is not None:
                return [lib.milkyway_techfile]
            else:
                return []

        return LibraryFilter.new("milkyway_tf", "Milkyway techfile", is_file=True, extraction_func=select_milkyway_tfs,
                                 extra_post_filter_funcs=[self.create_nonempty_check("Milkyway techfile")])

    @property
    def tlu_max_cap_filter(self) -> LibraryFilter:
        """TLU+ max cap filter."""

        def select_tlu_max_cap(lib: "Library") -> List[str]:
            if lib.tluplus_files is not None and lib.tluplus_files.max_cap is not None:
                return [lib.tluplus_files.max_cap]
            else:
                return []

        return LibraryFilter.new("tlu_max", "TLU+ max cap db", is_file=True, extraction_func=select_tlu_max_cap)

    @property
    def tlu_min_cap_filter(self) -> LibraryFilter:
        """TLU+ min cap filter."""

        def select_tlu_min_cap(lib: "Library") -> List[str]:
            if lib.tluplus_files is not None and lib.tluplus_files.min_cap is not None:
                return [lib.tluplus_files.min_cap]
            else:
                return []

        return LibraryFilter.new("tlu_min", "TLU+ min cap db", is_file=True, extraction_func=select_tlu_min_cap)
