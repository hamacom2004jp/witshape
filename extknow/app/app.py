from cmdbox.app import app
from extknow import version


def main(args_list:list=None):
    _app = app.CmdBoxApp.getInstance(appcls=ExtknowApp, ver=version)
    return _app.main(args_list)[0]

class ExtknowApp(app.CmdBoxApp):
    pass