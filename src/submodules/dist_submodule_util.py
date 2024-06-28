if __name__ == '__main__':
    import os,sys

    from PySide6.QtWidgets import QApplication

    proj_dir = r'E:/coding/pythonQt/'
    sys.path.append(proj_dir)
    sys.path.append(proj_dir+'src/submodules')

    from ui.ui_ren_suf import Ui_RenameSuffixWindow
    from rename_suffix import WindowRenameSuffix

    app = QApplication()
    window = WindowRenameSuffix()
    window.show()
    app.exec()
