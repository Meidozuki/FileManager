import logging
import shlex, subprocess

from .vbao_wrapper import vbao

CommandBaseWithOwner = vbao.CommandBaseWithOwner
CommandDirectCallMixin = vbao.CommandDirectCallMixin


class CommandClear(CommandBaseWithOwner):
    def execute(self):
        self.owner.clear()


class CommandSave(CommandBaseWithOwner, CommandDirectCallMixin):
    def execute(self):
        if self.args is not None:
            self.owner.saveData(*self.args)
        else:
            logging.error("Save command called without a path.")


class CommandLoad(CommandBaseWithOwner, CommandDirectCallMixin):
    def execute(self):
        if self.args is not None:
            filename = self.args[0]
            self.owner.loadData(filename)
        else:
            logging.error("Save command called without a path.")


class CommandAddTableRow(CommandBaseWithOwner, CommandDirectCallMixin):
    def execute(self):
        if self.args is not None:
            filename = self.args[0]
            self.owner.createOneLine(filename)

            self.args = None


class CommandUpdatePreviewImage(CommandBaseWithOwner, CommandDirectCallMixin):
    def setParameter(self, row: int, image: str):
        self.row = row
        self.image = image

    def execute(self):
        self.owner.updateImage(self.row, self.image)


class CommandUpdateTags(CommandBaseWithOwner, CommandDirectCallMixin):
    def setParameter(self, row: int, tag: str):
        self.row = row
        self.tag = tag

    def execute(self):
        self.owner.updateTags(self.row, self.tag)


class CommandFilterTags(CommandBaseWithOwner, CommandDirectCallMixin):
    def execute(self):
        self.owner.filterTag(*self.args)


class CommandClearTagFilters(CommandBaseWithOwner):
    def execute(self):
        self.owner.setProperty_vbao("filter_index", None)
        self.owner.onDataChanged()


class CommandOpenFile(CommandBaseWithOwner, CommandDirectCallMixin):
    def setParameter(self, open_program, overload):
        self.open_program = open_program
        self.overload = overload

    def execute(self):
        # todo: 路径有空格会报错，加上引号即可
        args = [self.open_program] + shlex.split(self.overload)
        print(args)
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            print(result.args)
            print(result.stderr)
