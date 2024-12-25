from cmdbox.app.features.web import cmdbox_web_gui
from witshape import version


class Gui(cmdbox_web_gui.Gui):
    def __init__(self, appcls, ver):
        super().__init__(appcls=appcls, ver=ver)
        self.version_info.append(dict(tabid='versions_witshape', title=version.__appid__,
                                      icon=f'assets/witshape/icon.png', url='versions_witshape'))
