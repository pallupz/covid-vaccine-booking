# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import pytest

from PyInstaller.compat import is_darwin, is_win
from PyInstaller.utils.tests import importorskip, xfail
from PyInstaller.utils.hooks import is_module_satisfies


@importorskip('jinxed')
def test_jinxed(pyi_builder):
    pyi_builder.test_source(
        '''
        import jinxed
        jinxed.setupterm('xterm')
        assert jinxed._terminal.TERM.terminfo is jinxed.terminfo.xterm
        '''
    )


def tensorflow_onedir_only(test):
    def wrapped(pyi_builder):
        if pyi_builder._mode != 'onedir':
            pytest.skip('Tensorflow tests support only onedir mode '
                        'due to potential distribution size.')
        test(pyi_builder)
    return wrapped

@importorskip('tensorflow')
@tensorflow_onedir_only
def test_tensorflow(pyi_builder):
    pyi_builder.test_source(
        """
        from tensorflow import *
        """
    )


@importorskip('tensorflow')
@tensorflow_onedir_only
def test_tensorflow_layer(pyi_builder):
    pyi_builder.test_script('pyi_lib_tensorflow_layer.py')


@importorskip('tensorflow')
@tensorflow_onedir_only
def test_tensorflow_mnist(pyi_builder):
    pyi_builder.test_script('pyi_lib_tensorflow_mnist.py')


@importorskip('trimesh')
def test_trimesh(pyi_builder):
    pyi_builder.test_source(
        """
        import trimesh
        """
    )


@importorskip('boto')
@xfail(reason='boto does not fully support Python 3')
def test_boto(pyi_builder):
    pyi_builder.test_script('pyi_lib_boto.py')


@xfail(reason='Issue #1844.')
@importorskip('boto3')
def test_boto3(pyi_builder):
    pyi_builder.test_source(
        """
        import boto3
        session = boto3.Session(region_name='us-west-2')

        # verify all clients
        for service in session.get_available_services():
            session.client(service)

        # verify all resources
        for resource in session.get_available_resources():
            session.resource(resource)
        """)


@xfail(reason='Issue #1844.')
@importorskip('botocore')
def test_botocore(pyi_builder):
    pyi_builder.test_source(
        """
        import botocore
        from botocore.session import Session
        session = Session()
        # verify all services
        for service in session.get_available_services():
            session.create_client(service, region_name='us-west-2')
        """)


@xfail(is_darwin, reason='Issue #1895.')
@importorskip('enchant')
def test_enchant(pyi_builder):
    pyi_builder.test_script('pyi_lib_enchant.py')


@importorskip('zmq')
def test_zmq(pyi_builder):
    pyi_builder.test_source(
        """
        import zmq
        print(zmq.__version__)
        print(zmq.zmq_version())
        # This is a problematic module and might cause some issues.
        import zmq.utils.strtypes
        """)


@importorskip('pylint')
def test_pylint(pyi_builder):
    pyi_builder.test_source(
        """
        # The following more obvious test doesn't work::
        #
        #   import pylint
        #   pylint.run_pylint()
        #
        # because pylint will exit with 32, since a valid command
        # line wasn't given. Instead, provide a valid command line below.

        from pylint.lint import Run
        Run(['-h'])
        """)


@importorskip('markdown')
def test_markdown(pyi_builder):
    # Markdown uses __import__ed extensions. Make sure these work by
    # trying to use the 'toc' extension..
    pyi_builder.test_source(
        """
        import markdown
        print(markdown.markdown('testing',
            extensions=['markdown.extensions.toc']))
        """)


@importorskip('lxml')
def test_lxml_isoschematron(pyi_builder):
    pyi_builder.test_source(
        """
        # The import of this module triggers the loading of some
        # required XML files.
        from lxml import isoschematron
        """)


@importorskip('openpyxl')
def test_openpyxl(pyi_builder):
    pyi_builder.test_source(
        """
        # Test the hook to openpyxl
        from openpyxl import __version__
        """)


@importorskip('pyodbc')
def test_pyodbc(pyi_builder):
    pyi_builder.test_source(
        """
        # pyodbc is a binary Python module. On Windows when installed with easy_install
        # it is installed as zipped Python egg. This binary module is extracted
        # to PYTHON_EGG_CACHE directory. PyInstaller should find the binary there and
        # include it with frozen executable.
        import pyodbc
        """)


@importorskip('pyttsx')
def test_pyttsx(pyi_builder):
    pyi_builder.test_source(
        """
        # Basic code example from pyttsx tutorial.
        # http://packages.python.org/pyttsx/engine.html#examples
        import pyttsx
        engine = pyttsx.init()
        engine.say('Sally sells seashells by the seashore.')
        engine.say('The quick brown fox jumped over the lazy dog.')
        engine.runAndWait()
        """)


@importorskip('pycparser')
def test_pycparser(pyi_builder):
    pyi_builder.test_script('pyi_lib_pycparser.py')


@importorskip('Crypto')
def test_pycrypto(pyi_builder):
    pyi_builder.test_source(
        """
        import binascii
        from Crypto.Cipher import AES
        BLOCK_SIZE = 16
        print('AES null encryption, block size', BLOCK_SIZE)
        # Just for testing functionality after all
        print('HEX', binascii.hexlify(
            AES.new(b"\\0" * BLOCK_SIZE, AES.MODE_ECB).encrypt(b"\\0" * BLOCK_SIZE)))
        from Crypto.PublicKey import ECC
        """)


@importorskip('Cryptodome')
def test_cryptodome(pyi_builder):
    pyi_builder.test_source(
        """
        from Cryptodome import Cipher
        from Cryptodome.PublicKey import ECC
        print('Cryptodome Cipher Module:', Cipher)
        """)


@importorskip('h5py')
def test_h5py(pyi_builder):
    pyi_builder.test_source("""
        import h5py
        """)


@importorskip('unidecode')
def test_unidecode(pyi_builder):
    pyi_builder.test_source("""
        from unidecode import unidecode

        # Unidecode should not skip non-ASCII chars if mappings for them exist.
        assert unidecode(u"kožušček") == "kozuscek"
        """)


@importorskip('pinyin')
def test_pinyin(pyi_builder):
    pyi_builder.test_source("""
        import pinyin
        """)


@importorskip('uvloop')
@pytest.mark.darwin
@pytest.mark.linux
def test_uvloop(pyi_builder):
    pyi_builder.test_source("import uvloop")


@importorskip('web3')
def test_web3(pyi_builder):
    pyi_builder.test_source("import web3")


@importorskip('phonenumbers')
def test_phonenumbers(pyi_builder):
    pyi_builder.test_source("""
        import phonenumbers

        number = '+17034820623'
        parsed_number = phonenumbers.parse(number)

        assert(parsed_number.country_code == 1)
        assert(parsed_number.national_number == 7034820623)
        """)


@importorskip('pendulum')
def test_pendulum(pyi_builder):
    pyi_builder.test_source("""
        import pendulum

        print(pendulum.now().isoformat())
        """)


@importorskip('argon2')
def test_argon2(pyi_builder):
    pyi_builder.test_source("""
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        hash = ph.hash("s3kr3tp4ssw0rd")
        ph.verify(hash, "s3kr3tp4ssw0rd")
        """)


@importorskip('pytest')
def test_pytest_runner(pyi_builder):
    """
    Check if pytest runner builds correctly.
    """
    pyi_builder.test_source(
        """
        import pytest
        import sys
        sys.exit(pytest.main(['--help']))
        """)


@importorskip('eel')
def test_eel(pyi_builder):
    pyi_builder.test_source("import eel")


@importorskip('sentry_sdk')
def test_sentry(pyi_builder):
    pyi_builder.test_source(
        """
        import sentry_sdk
        sentry_sdk.init()
        """)


@importorskip('iminuit')
def test_iminuit(pyi_builder):
    pyi_builder.test_source("""
        from iminuit import Minuit
        """)


@importorskip('av')
def test_av(pyi_builder):
    pyi_builder.test_source("""
        import av
        """)


@importorskip('passlib')
def test_passlib(pyi_builder):
    pyi_builder.test_source("""
        import passlib.apache
        """)


@importorskip('publicsuffix2')
def test_publicsuffix2(pyi_builder):
    pyi_builder.test_source("""
        import publicsuffix2
        publicsuffix2.PublicSuffixList()
        """)


@importorskip('pydivert')
def test_pydivert(pyi_builder):
    pyi_builder.test_source("""
        import pydivert
        pydivert.WinDivert.check_filter("inbound")
        """)


@importorskip('skimage')
@pytest.mark.skipif(not is_module_satisfies('skimage >= 0.16.0'),
                    reason='The test supports only skimage 0.16.0 or newer.')
@pytest.mark.parametrize('submodule', [
    'color', 'data', 'draw', 'exposure', 'feature', 'filters', 'future',
    'graph', 'io', 'measure', 'metrics', 'morphology', 'registration',
    'restoration', 'segmentation', 'transform', 'util', 'viewer'
])
def test_skimage(pyi_builder, submodule):
    pyi_builder.test_source("""
        import skimage.{0}
        """.format(submodule))


@importorskip('sklearn')
@pytest.mark.skipif(not is_module_satisfies('sklearn >= 0.21'),
                    reason='The test supports only scikit-learn >= 0.21.')
@pytest.mark.parametrize('submodule', [
    'calibration', 'cluster', 'covariance', 'cross_decomposition',
    'datasets', 'decomposition', 'dummy', 'ensemble', 'exceptions',
    'experimental', 'externals', 'feature_extraction',
    'feature_selection', 'gaussian_process', 'inspection',
    'isotonic', 'kernel_approximation', 'kernel_ridge',
    'linear_model', 'manifold', 'metrics', 'mixture',
    'model_selection', 'multiclass', 'multioutput',
    'naive_bayes', 'neighbors', 'neural_network', 'pipeline',
    'preprocessing', 'random_projection', 'semi_supervised',
    'svm', 'tree', 'discriminant_analysis', 'impute', 'compose'
])
def test_sklearn(pyi_builder, submodule):
    pyi_builder.test_source("""
        import sklearn.{0}
        """.format(submodule))


@importorskip('win32ctypes')
@pytest.mark.skipif(not is_win, reason='pywin32-ctypes is supported only on Windows')
@pytest.mark.parametrize('submodule', ['win32api', 'win32cred', 'pywintypes'])
def test_pywin32ctypes(pyi_builder, submodule):
    pyi_builder.test_source("""
        from win32ctypes.pywin32 import {0}
        """.format(submodule))


@importorskip('pyproj')
@pytest.mark.skipif(not is_module_satisfies('pyproj >= 2.1.3'),
                    reason='The test supports only pyproj >= 2.1.3.')
def test_pyproj(pyi_builder):
    pyi_builder.test_source("""
        import pyproj
        tf = pyproj.Transformer.from_crs(
            7789,
            8401
        )
        result = tf.transform(
            xx=3496737.2679,
            yy=743254.4507,
            zz=5264462.9620,
            tt=2019.0
        )
        print(result)
        """)


@importorskip('pydantic')
def test_pydantic(pyi_builder):
    pyi_builder.test_source("""
        import pydantic
        """)


def torch_onedir_only(test):
    def wrapped(pyi_builder):
        if pyi_builder._mode != 'onedir':
            pytest.skip('PyTorch tests support only onedir mode '
                        'due to potential distribution size.')
        test(pyi_builder)
    return wrapped


@importorskip('torchvision')
@torch_onedir_only
def test_torchvision_nms(pyi_builder):
    pyi_builder.test_source("""
        import torch
        import torchvision
        # boxes: Nx4 tensor (x1, y1, x2, y2)
        boxes = torch.tensor([
            [0.0, 0.0, 1.0, 1.0],
            [0.45, 0.0, 1.0, 1.0],
        ])
        # scores: Nx1 tensor
        scores = torch.tensor([
            1.0,
            1.1
        ])
        keep = torchvision.ops.nms(boxes, scores, 0.5)
        # The boxes have IoU of 0.55, and the second one has a slightly
        # higher score, so we expect it to be kept while the first one
        # is discarded.
        assert keep == 1
    """)


@importorskip('googleapiclient')
def test_googleapiclient(pyi_builder):
    pyi_builder.test_source("""
        from googleapiclient.discovery import build
        """)
