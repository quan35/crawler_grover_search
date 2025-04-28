"""
项目主程序入口
仅用于启动桌面GUI。
"""
import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QTimer

# 版本信息
VERSION = "1.1.0"

# 添加日志文件输出
import logging
logging.basicConfig(
    filename='app_error.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 全局变量，保持对主窗口的引用，防止被垃圾回收
main_window = None

def check_dependencies():
    """检查项目依赖是否已安装"""
    required_packages = ['bs4', 'PyQt5', 'qiskit', 'numpy', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
            logging.error(f"缺少依赖包: {package}")
    
    if missing_packages:
        print("错误：缺少必要的依赖包！")
        print(f"请使用以下命令安装缺失的包：")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def show_error(error_msg):
    """显示错误对话框"""
    from PyQt5.QtWidgets import QMessageBox
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)
    error_box.setWindowTitle("错误")
    error_box.setText("程序启动失败")
    error_box.setInformativeText(error_msg)
    error_box.setDetailedText(traceback.format_exc())
    error_box.setStandardButtons(QMessageBox.Ok)
    error_box.exec_()
    
    # 同时记录到日志
    logging.error(f"错误: {error_msg}\n{traceback.format_exc()}")

def main():
    """主程序入口"""
    try:
        logging.info("程序开始启动")
        
        # 检查依赖
        if not check_dependencies():
            sys.exit(1)
        
        # 初始化应用
        app = QApplication(sys.argv)
        app.setApplicationName("Grover量子搜索与网络聚合系统")
        app.setApplicationVersion(VERSION)
        
        # 设置应用样式
        app.setStyle("Fusion")
        logging.info("应用初始化完成")
        
        # 显示启动画面
        splash_path = os.path.join(os.path.dirname(__file__), 'pic.ico')
        if os.path.exists(splash_path):
            logging.info(f"加载启动画面: {splash_path}")
            splash_pixmap = QPixmap(splash_path)
            if not splash_pixmap.isNull():
                splash = QSplashScreen(splash_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                splash.show()
                app.processEvents()
        else:
            logging.warning(f"启动画面不存在: {splash_path}")
        
        # 直接加载主窗口，而不是使用延迟
        load_main_window(app, splash if 'splash' in locals() else None)
        
        logging.info("进入主事件循环")
        return app.exec_()
    
    except Exception as e:
        error_msg = f"程序启动出错: {str(e)}"
        logging.critical(error_msg)
        logging.exception(e)
        show_error(error_msg)
        return 1

def load_main_window(app, splash=None):
    """加载主窗口"""
    global main_window
    try:
        logging.info("开始加载主窗口")
        from gui.main_window import MainWindow
        logging.info("成功导入MainWindow类")
        
        main_window = MainWindow()
        logging.info("MainWindow实例创建成功")
        
        main_window.setWindowTitle(f"Grover量子搜索与网络聚合系统 v{VERSION}")
        
        # 如果有启动画面，先隐藏
        if splash:
            logging.info("关闭启动画面")
            splash.finish(main_window)
        
        # 显示主窗口
        logging.info("显示主窗口")
        main_window.show()
        
        # 显示欢迎信息
        QTimer.singleShot(500, lambda: main_window.statusBar().showMessage(f"欢迎使用 Grover量子搜索系统 v{VERSION}", 5000))
        
        logging.info("主窗口加载完成")
        
    except Exception as e:
        error_msg = f"加载主窗口失败: {str(e)}"
        logging.critical(error_msg)
        logging.exception(e)
        show_error(error_msg)
        app.quit()

if __name__ == "__main__":
    exit_code = main()
    logging.info(f"程序退出，退出码：{exit_code}")
    sys.exit(exit_code)
