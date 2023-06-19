#!/usr/bin/env python

import os
import platform
import struct
import subprocess  # nosec B404 only used without user inputs
import locale

import sys
import importlib
import argparse


def get_sys_info():
    """Returns system information as a dict"""

    blob = []

    # get full commit hash
    commit = None
    if os.path.isdir(".git") and os.path.isdir("argopy"):
        try:
            pipe = subprocess.Popen(  # nosec No user provided input to control here
                'git log --format="%H" -n 1'.split(" "),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            so, serr = pipe.communicate()
        except Exception:
            pass
        else:
            if pipe.returncode == 0:
                commit = so
                try:
                    commit = so.decode("utf-8")
                except ValueError:
                    pass
                commit = commit.strip().strip('"')

    blob.append(("commit", commit))

    try:
        (sysname, nodename, release, version_, machine, processor) = platform.uname()
        blob.extend(
            [
                ("python", sys.version),
                ("python-bits", struct.calcsize("P") * 8),
                ("OS", "%s" % (sysname)),
                ("OS-release", "%s" % (release)),
                ("machine", "%s" % (machine)),
                ("processor", "%s" % (processor)),
                ("byteorder", "%s" % sys.byteorder),
                ("LC_ALL", "%s" % os.environ.get("LC_ALL", "None")),
                ("LANG", "%s" % os.environ.get("LANG", "None")),
                ("LOCALE", "%s.%s" % locale.getlocale()),
            ]
        )
    except Exception:
        pass

    return blob


def netcdf_and_hdf5_versions():
    libhdf5_version = None
    libnetcdf_version = None
    try:
        import netCDF4

        libhdf5_version = netCDF4.__hdf5libversion__
        libnetcdf_version = netCDF4.__netcdf4libversion__
    except ImportError:
        try:
            import h5py

            libhdf5_version = h5py.version.hdf5_version
        except ImportError:
            pass
    return [("libhdf5", libhdf5_version), ("libnetcdf", libnetcdf_version)]


def show_versions(file=sys.stdout, conda=False, free=False, core=False):  # noqa: C901
    """ Print versions of dependencies

    Parameters
    ----------
    file : file-like, optional
        print to the given file-like object. Defaults to sys.stdout.
    conda: bool, optional
        format versions to be copy/pasted on a conda environment file (default, False)
    """
    sys_info = get_sys_info()

    try:
        sys_info.extend(netcdf_and_hdf5_versions())
    except Exception as e:
        print(f"Error collecting netcdf / hdf5 version: {e}")

    DEPS = {
        'core': sorted([
            ("xarray", lambda mod: mod.__version__),
            ("netCDF4", lambda mod: mod.__version__),
            ("fsspec", lambda mod: mod.__version__),
            ("scipy", lambda mod: mod.__version__),
            ("aiohttp", lambda mod: mod.__version__),
            # ("argopy", lambda mod: mod.__version__),
        ]),
        'util': sorted([
            ("gsw", lambda mod: mod.__version__),
            ("tqdm", lambda mod: mod.__version__),
            # ("motuclient", lambda mod: mod.__version__),
        ]),
        'stat': sorted([
            ("dask", lambda mod: mod.__version__),
            ("distributed", lambda mod: mod.__version__),
            ("sklearn", lambda mod: mod.__version__),
            ("xhistogram", lambda mod: mod.__version__),
            ("dask_ml", lambda mod: mod.__version__),
        ]),
        'plot': sorted([
            ("matplotlib", lambda mod: mod.__version__),
            ("regionmask", lambda mod: mod.__version__),
            ("cartopy", lambda mod: mod.__version__),
            ("seaborn", lambda mod: mod.__version__),
            ("ipykernel", lambda mod: mod.__version__),
        ]),

        'dev': sorted([
            ("numpy", lambda mod: mod.__version__),  # will come with xarray and pandas
            ("pandas", lambda mod: mod.__version__),  # will come with xarray
            ("pip", lambda mod: mod.__version__),
        ]),

        'pip': sorted([
            ("argopy", lambda mod: mod.__version__),
            ("pyxpcm", lambda mod: mod.__version__),
            ("motuclient", lambda mod: mod.__version__),
        ]),
    }

    def fix_modname(name):
        if name == 'sklearn':
            return "scikit-learn"
        elif name == 'dask_ml':
            return "dask-ml"
        else:
            return name

    # Get versions:
    DEPS_blob = {}
    for level in DEPS.keys():
        deps = DEPS[level]
        deps_blob = list()
        for (modname, ver_f) in deps:
            try:
                if modname in sys.modules:
                    mod = sys.modules[modname]
                else:
                    mod = importlib.import_module(modname)
            except Exception:
                deps_blob.append((fix_modname(modname), '-'))
            else:
                try:
                    ver = ver_f(mod)
                    deps_blob.append((fix_modname(modname), ver))
                except Exception:
                    deps_blob.append((fix_modname(modname), "installed"))
        DEPS_blob[level] = deps_blob

    # Print:
    if conda:
        # print("\nSYSTEM", file=file)
        print("\n------", file=file)
        print(f"  - python = {sys.version.split('|')[0].strip()}", file=file)

        for level in DEPS_blob:
            print("\n# %s:" % level.upper(), file=file)
            deps_blob = DEPS_blob[level]
            if level != 'pip':
                for k, stat in deps_blob:
                    kf = k.replace("_", "-")
                    comment = ' ' if stat != '-' else '# '
                    if core and 'EXT' in level.upper():
                        comment = '# '
                    if not free:
                        print(f"{comment} - {kf} = {stat}",
                              file=file)  # Format like a conda env line, useful to update ci/requirements
                    else:
                        print(f"{comment} - {kf}", file=file)
            else:
                #   - pip:
                #       - aioresponses==0.7.4
                print("  - pip:", file=file)
                for k, stat in deps_blob:
                    if k is not None:
                        kf = k.replace("_", "-")
                    else:
                        kf = k
                    comment = '     ' if stat != '-' else '     # '
                    if not free:
                        print(f"{comment} - {kf} == {stat}",
                              file=file)  # Format like a conda env line, useful to update ci/requirements
                    else:
                        print(f"{comment} - {kf}", file=file)

    else:

        print("\nSYSTEM", file=file)
        print("------", file=file)
        for k, stat in sys_info:
            print(f"{k}: {stat}", file=file)

        for level in DEPS_blob:
            if conda:
                print("\n# %s:" % level.upper(), file=file)
            else:
                title = "INSTALLED VERSIONS: %s" % level.upper()
                print("\n%s" % title, file=file)
                print("-" * len(title), file=file)
            deps_blob = DEPS_blob[level]
            for k, stat in deps_blob:
                if conda:
                    kf = k.replace("_", "-")
                    comment = ' ' if stat != '-' else '# '
                    print(f"{comment} - {kf} = {stat}",
                          file=file)  # Format like a conda env line, useful to update ci/requirements
                else:
                    print("{:<12}: {:<12}".format(k, stat), file=file)


def setup_args():
    icons_help_string = """This script display dependencies versions of current environment"""

    parser = argparse.ArgumentParser(description='Dpendencies versions',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="%s\n(c) Argo-France/Ifremer/LOPS, 2023" % icons_help_string)

    parser.add_argument("-c", "--conda", help="Print package versions for conda yml files", action="store_true")
    parser.add_argument("--free", help="Just print package lists for FREE conda yml files", action="store_true")
    parser.add_argument("--core", help="Just print CORE package lists for conda yml files", action="store_true")

    return parser


if __name__ == '__main__':
    ARGS = setup_args().parse_args()
    show_versions(conda=ARGS.conda if ARGS.conda else False,
                  free=ARGS.free if ARGS.free else False,
                  core=ARGS.core if ARGS.core else False)

