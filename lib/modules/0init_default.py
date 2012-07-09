# coding=utf-8

class DefaultInit:
    def __init__(self, remote):
        self._remote = remote
        self._remote.set_dispatch(iface.dispatch.get_line)
        self._pkg_id = self._remote.connect('package', self._pkg_cb)
    def _pkg_cb(self, remote, pkg)
        pkg = pkg.strip()

iface.initializer.default = DefaultInit
