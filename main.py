"""
项目主程序入口
仅用于启动桌面GUI。
"""

if __name__ == "__main__":
    from gui.main_window import MainWindow
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
