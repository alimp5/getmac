# -*- coding: utf-8 -*-

import io
import sys
from os import path

import pytest

from getmac import get_mac_address, getmac

PY2 = sys.version_info[0] == 2
MAC_RE_COLON = r'([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})'
MAC_RE_DASH = r'([0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5})'


@pytest.fixture
def get_sample():
    def _get_sample(sample_path):
        sdir = path.realpath(path.join(path.dirname(__file__), '..', 'samples'))
        with io.open(path.join(sdir, sample_path), 'rt',
                     newline='', encoding='utf-8') as f:
            return f.read()
    return _get_sample


# def test_linux_ifconfig(mocker, get_sample):
#     # content = get_sample('ifconfig.out')
#     getmac.getmac.WINDOWS = False
#     getmac.getmac.OSX = False
#     getmac.getmac.WSL = False
#     getmac.getmac.LINUX = True
#     # mocker.patch
#     assert '74:d4:35:e9:45:71' == getmac.get_mac_address(interface='eth0')


# def test_linux_ip_link(mocker, get_sample):
#     # content = get_sample('ip_link_list.out')
#     assert '74:d4:35:e9:45:71' == getmac.get_mac_address(interface='eth0')


# def test_osx_ifconfig(mocker, get_sample):
#     # content = get_sample(path.join('OSX', 'ifconfig.out'))
#     pass


def test_get_mac_address_localhost():
    assert get_mac_address(hostname='localhost') == '00:00:00:00:00:00'
    assert get_mac_address(ip='127.0.0.1') == '00:00:00:00:00:00'
    assert get_mac_address(
        hostname='localhost', network_request=False) == '00:00:00:00:00:00'


def test_search(get_sample):
    text = get_sample('ifconfig.out')
    regex = r'HWaddr ' + MAC_RE_COLON
    assert getmac._search(regex, text, 0) == '74:d4:35:e9:45:71'


def test_popen(mocker):
    mocker.patch('getmac.getmac.PATH', [])
    m = mocker.patch('getmac.getmac._call_proc', return_value='SUCCESS')
    assert getmac._popen('TESTCMD', 'ARGS') == 'SUCCESS'
    m.assert_called_once_with('TESTCMD', 'ARGS')


def test_call_proc_windows(mocker):
    mocker.patch('getmac.getmac.DEVNULL', 'DEVNULL')
    mocker.patch('getmac.getmac.ENV', 'ENV')
    mocker.patch('getmac.getmac.WINDOWS', True)

    m = mocker.patch('getmac.getmac.check_output', return_value='WINSUCCESS')
    assert getmac._call_proc('CMD', 'arg') == 'WINSUCCESS'
    m.assert_called_once_with('CMD' + ' ' + 'arg', stderr='DEVNULL', env='ENV')

    mocker.patch('getmac.getmac.WINDOWS', False)
    m = mocker.patch('getmac.getmac.check_output', return_value='YAY')
    assert getmac._call_proc('CMD', 'arg1 arg2') == 'YAY'
    m.assert_called_once_with(['CMD', 'arg1', 'arg2'], stderr='DEVNULL', env='ENV')


def test_windows_ctypes_host(mocker):
    # mocker.patch.object(getmac, 'WINDOWS', True)
    pass


def test_fcntl_iface(mocker):
    pass


def test_uuid_ip(mocker):
    pass


def test_uuid_lanscan_iface(mocker):
    mocker.patch('uuid._find_mac', return_value=2482700837424)
    assert getmac._uuid_lanscan_iface('en1') == '02:42:0C:80:62:30'
    mocker.patch('uuid._find_mac', return_value=None)
    assert getmac._uuid_lanscan_iface('en0') is None


def test_uuid_convert():
    assert getmac._uuid_convert(2482700837424) == '02:42:0C:80:62:30'


def test_read_sys_iface_file(mocker):
    mocker.patch('getmac.getmac._read_file', return_value='00:0c:29:b5:72:37\n')
    assert getmac._read_sys_iface_file('ens33') == '00:0c:29:b5:72:37\n'
    mocker.patch('getmac.getmac._read_file', return_value=None)
    assert getmac._read_sys_iface_file('ens33') is None


def test_read_arp_file(mocker, get_sample):
    data = get_sample('ubuntu_18.10/proc_net_arp.txt')
    mocker.patch('getmac.getmac._read_file', return_value=data)
    assert getmac._read_arp_file('192.168.16.2') == '00:50:56:e1:a8:4a'
    assert getmac._read_arp_file('192.168.16.254') == '00:50:56:e8:32:3c'
    assert getmac._read_arp_file('192.168.95.1') == '00:50:56:c0:00:0a'
    assert getmac._read_arp_file('192.168.95.254') == '00:50:56:fa:b7:54'


def test_read_file_return(mocker, get_sample):
    data = get_sample('ifconfig.out')
    mock_open = mocker.mock_open(read_data=data)
    if PY2:
        mocker.patch('__builtin__.open', mock_open)
    else:
        mocker.patch('builtins.open', mock_open)
    assert getmac._read_file('ifconfig.out') == data
    mock_open.assert_called_once_with('ifconfig.out')


def test_read_file_not_exist():
    assert getmac._read_file('DOESNOTEXIST') is None


def test_get_default_iface_linux(mocker, get_sample):
    data = get_sample('ubuntu_18.10/proc_net_route.txt')
    mocker.patch('getmac.getmac._read_file', return_value=data)
    assert getmac._get_default_iface_linux() == 'ens33'


def test_hunt_linux_default_iface(mocker, get_sample):
    data = get_sample('ubuntu_18.10/proc_net_route.txt')
    mocker.patch('getmac.getmac._read_file', return_value=data)
    assert getmac._hunt_linux_default_iface() == 'ens33'


def test_fetch_ip_using_dns(mocker):
    m = mocker.patch('socket.socket')
    m.return_value.getsockname.return_value = ('1.2.3.4', 51327)
    assert getmac._fetch_ip_using_dns() == '1.2.3.4'
