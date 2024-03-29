import shlex, subprocess

from .vbao_wrapper import vbao


class CommandTryAddClass(vbao.CommandBaseWithOwner):
    def setParameter(self, filename, *args, **kwargs):
        self.args = [filename]

    def execute(self):
        if self.args is not None:
            filename = self.args[0]
            success = self.owner.createOneLine(filename)
            self.owner.triggerCommandNotifications("add_new", success)

            self.args = None

class CommandOpenFile(vbao.CommandBaseWithOwner):
    def setParameter(self, *args, **kwargs):
        self.open_program = 'explorer'
        self.overload = None

    def execute(self):
        args = [self.open_program] + shlex.split(self.overload)
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            print(result.args)
            print(result.stderr)