# coding=utf-8

class DefaultInit:
    def __init__(self, remote):
        self._remote = remote
        self._remote.set_dispatch(self._dispatch)
        self.send('RUBUSY?')
    def _dispatch(self, buff):
        buff = buff.lstrip()
        if not buff:
            return ('', '')
        if buff[0].isalpha():
            self._remote.set_dispatch(iface.dispatch.get_line)
            self._remote.set_name('zwicky')
            return iface.dispatch.get_line(buff)
        if buff[0] in '([{':
            pkg, left = iface.dispatch.get_json(buff)
            if not pkg:
                return pkg, left
            self._remote.set_dispatch(iface.dispatch.get_json)
            import json
            try:
                obj = json.loads(pkg)
            except ValueError:
                self._remote.set_name(None)
                return pkg, left
            if not 'name' in obj:
                # don't really like this
                self._remote.set_name('purcell')
            else:
                self._remote.set_name(obj['name'])
            return pkg, left
        self._remote.set_name(None)
        return super()._do_dispatch(buff)

iface.initializer.default = DefaultInit
