from cmdbox.app import app
from witshape import version


def main(args_list:list=None):
    _app = app.CmdBoxApp.getInstance(appcls=WitshapeApp, ver=version)
    return _app.main(args_list)[0]

class WitshapeApp(app.CmdBoxApp):
    pass