import random
import shutil
import string
import subprocess

import stem.process
import tempfile

from stem import Signal
from stem.control import Controller
from stem.util import term


class TorSession:
    def __init__(self, socks_port=None, data_directory=None, control_port=None, control_password=None):
        if socks_port is None:
            socks_port = 9050

        if control_port is None:
            control_port = 9051

        if data_directory is None:
            data_directory = tempfile.mkdtemp()

        if control_password is None:
            control_password = self.generate_random_password(20)

        self.socks_port = socks_port
        self.control_port = control_port
        self.data_directory = data_directory
        self.control_password = control_password

        self.tor_process = stem.process.launch_tor_with_config(
            config={
                'SocksPort': str(self.socks_port),
                'ControlPort': str(self.control_port),
                'HashedControlPassword': self.generate_tor_password(self.control_password),
                'DataDirectory': self.data_directory
            },
            init_msg_handler=self.print_bootstrap_lines
        )

    def renew_identity(self):
        with Controller.from_port(port=self.control_port) as controller:
            controller.authenticate(password=self.control_password)
            controller.signal(Signal.NEWNYM)

    def terminate(self):
        if self.tor_process is None:
            return
        self.tor_process.terminate()
        shutil.rmtree(self.data_directory, ignore_errors=True)

    @staticmethod
    def generate_tor_password(pwd):
        p = subprocess.Popen(['tor', '--hash-password', str(pwd)], stdout=subprocess.PIPE)
        pwd, error = p.communicate()

        if error is not None:
            raise Exception(error)

        return pwd.strip()

    @staticmethod
    def print_bootstrap_lines(line):
        if "Bootstrapped " in line:
            print(term.format(line, term.Color.BLUE))

    @staticmethod
    def generate_random_password(length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    @property
    def proxies(self):
        return {
            'http': 'socks5://127.0.0.1:{}'.format(self.socks_port),
            'https': 'socks5://127.0.0.1:{}'.format(self.socks_port)
        }

    def __del__(self):
        self.terminate()
