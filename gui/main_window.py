"""
Main window interface (implemented with PyQt5)
Supports keyword input, web crawling, aggregation, database storage, classical and Grover search, result visualization.
"""
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTextBrowser, QMessageBox, QComboBox,
    QTabWidget, QGridLayout, QFrame, QSplitter, QProgressBar, QToolButton,
    QListWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPalette
import os
import sys
import webbrowser
import urllib.parse
import time
from web_crawler.aggregator import aggregate_and_deduplicate
from database import LocalDatabase
from classical_search import classical_linear_search
from grover.grover_core import grover_search, simulate_and_plot

class CrawlThread(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    
    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword
    
    def run(self):
        from web_crawler.multi_crawler import multi_source_crawl
        data = multi_source_crawl(self.keyword, progress_callback=self.progress.emit)
        self.finished.emit(data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grover Quantum Search and Web Aggregation Demo")
        self.setGeometry(300, 100, 1200, 950)
        # 获取图标路径
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pic.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Initialize database
        self.db = LocalDatabase()
        
        # Set application theme colors
        self.setPalette(self.create_dark_palette() if self.is_dark_mode_preferred() else self.create_light_palette())
        
        # Initialize UI
        self.init_ui()
        
        # Status bar shows database status
        self.update_statusbar()
    
    def is_dark_mode_preferred(self):
        """检测系统是否偏好深色模式（简单实现，实际可以基于系统API）"""
        return False  # 默认返回浅色模式
    
    def create_light_palette(self):
        """创建浅色主题调色板"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 247))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(233, 231, 237))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(235, 235, 235))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        return palette
    
    def create_dark_palette(self):
        """创建深色主题调色板"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(56, 56, 56))
        palette.setColor(QPalette.Text, QColor(212, 212, 212))
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        return palette

    def init_ui(self):
        # 设置全局QSS美化
        self.setStyleSheet('''
            QWidget {
                font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
                font-size: 15px;
            }
            QLabel#TitleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2060a0;
                padding: 20px 0 15px 0;
                qproperty-alignment: AlignCenter;
            }
            QLineEdit {
                border: 1.5px solid #b0bfe6;
                border-radius: 8px;
                padding: 8px 12px;
                background: #fff;
                font-size: 16px;
                selection-background-color: #3d88ee;
                height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #337ecc;
                background: #f0f7ff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4696e5, stop:1 #337ecc);
                color: #2ad56e;
                border-radius: 8px;
                font-size: 15px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 100px;
                height: 36px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d88ee, stop:1 #205eaa);
            }
            QPushButton:pressed {
                background: #205eaa;
            }
            QPushButton#quantumDetailBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4696e5, stop:1 #2060a0);
                border: 2px solid #1c4e8f;
            }
            QPushButton#quantumDetailBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d88ee, stop:1 #19508c);
            }
            QPushButton#quantumDetailBtn:pressed {
                background: #19508c;
            }
            QComboBox {
                border: 1.5px solid #b0bfe6;
                border-radius: 8px;
                padding: 8px 12px;
                background: #fff;
                font-size: 15px;
                height: 20px;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1.5px solid #337ecc;
                background: #f0f7ff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 25px;
                border-left: 1px solid #b0bfe6;
                padding-right: 5px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #b0bfe6;
                background: white;
                selection-background-color: #e0e8f5;
                min-width: 400px;
                max-width: 600px;
                padding: 5px;
            }
            QComboBox::item {
                height: 30px;
                padding-left: 10px;
            }
            QComboBox::item:hover {
                background-color: #e0e8f5;
            }
            QComboBox::item:selected {
                background-color: #d0d8f0;
            }
            QTextBrowser {
                background: #fafdff;
                border-radius: 12px;
                border: 1.5px solid #b0bfe6;
                font-size: 15px;
                padding: 15px;
                color: #222;
                selection-background-color: #3d88ee;
                selection-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #b0bfe6;
                border-radius: 6px;
                top: -1px;
                background: #fafdff;
            }
            QTabBar::tab {
                background: #e6eaf2;
                border: 1px solid #b0bfe6;
                border-bottom-color: #b0bfe6;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                color: #555;
            }
            QTabBar::tab:selected {
                background: #fafdff;
                border-bottom-color: #fafdff;
                color: #2060a0;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QProgressBar {
                border: 1px solid #b0bfe6;
                border-radius: 5px;
                text-align: center;
                background: #fafdff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4696e5, stop:1 #337ecc);
                width: 10px;
                margin: 0.5px;
            }
            QStatusBar {
                background: #f6f8fa;
                color: #555;
            }
            QToolButton {
                background: transparent;
                border: none;
                padding: 3px;
            }
            QToolButton:hover {
                background: rgba(0, 0, 0, 0.05);
                border-radius: 4px;
            }
            QFrame#line {
                background-color: #b0bfe6;
                max-height: 1px;
            }
        ''')
        
        # 创建主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 10, 20, 20)
        main_layout.setSpacing(15)
        
        # 创建标题和副标题
        title_layout = QVBoxLayout()
        title = QLabel("Grover Quantum Search and Web Aggregation System")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("Combining quantum computing and classical search technologies for efficient information retrieval")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 16px; padding-bottom: 10px;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        main_layout.addLayout(title_layout)
        
        # 添加水平分割线
        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 标签页1: 搜索与抓取
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        search_layout.setContentsMargins(15, 20, 15, 15)
        search_layout.setSpacing(15)
        
        # 关键词输入区域
        input_frame = QFrame()
        input_frame.setFrameShape(QFrame.StyledPanel)
        input_frame.setStyleSheet("background: #f6f8fa; border-radius: 10px; padding: 15px;")
        input_layout = QVBoxLayout(input_frame)
        
        # 关键词输入标题
        input_title = QLabel("Web Content Crawling")
        input_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2060a0;")
        input_layout.addWidget(input_title)
        
        # 关键词输入与按钮
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel("Keyword:")
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("Enter search keyword")
        # 添加回车键响应
        self.keyword_edit.returnPressed.connect(self.on_crawl)
        
        self.crawl_btn = QPushButton("Crawl Web Content")
        self.crawl_btn.setIcon(QIcon.fromTheme("search"))
        self.crawl_btn.clicked.connect(self.on_crawl)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_edit, 1)  # 1是伸展因子
        keyword_layout.addWidget(self.crawl_btn)
        
        input_layout.addLayout(keyword_layout)
        input_layout.addWidget(self.progress_bar)
        search_layout.addWidget(input_frame)
        
        # 目标搜索区域
        target_frame = QFrame()
        target_frame.setFrameShape(QFrame.StyledPanel)
        target_frame.setStyleSheet("background: #f6f8fa; border-radius: 10px; padding: 15px;")
        target_layout = QVBoxLayout(target_frame)
        
        # 目标搜索标题
        target_title = QLabel("Target Search")
        target_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2060a0;")
        target_layout.addWidget(target_title)
        
        # 目标搜索输入与按钮
        search_input_layout = QHBoxLayout()
        target_label = QLabel("Target:")
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("Enter target to find")
        # 添加回车键响应
        self.target_edit.returnPressed.connect(self.on_search)
        
        self.alg_combo = QComboBox()
        self.alg_combo.addItems(["Classical Search", "Grover Quantum Search"])
        self.alg_combo.setStyleSheet("padding-right: 15px;")
        
        self.search_btn = QPushButton("Search")
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.search_btn.clicked.connect(self.on_search)
        
        search_input_layout.addWidget(target_label)
        search_input_layout.addWidget(self.target_edit, 1)
        search_input_layout.addWidget(self.alg_combo)
        search_input_layout.addWidget(self.search_btn)
        
        # 历史记录区域
        history_layout = QHBoxLayout()
        history_label = QLabel("Search History:")
        self.history_combo = QComboBox()
        self.history_combo.setMinimumWidth(500)  # 增加最小宽度
        self.history_combo.setMaximumHeight(45)  # 控制高度
        self.history_combo.setMaxVisibleItems(10)  # 设置最大可见项数
        self.history_combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.history_combo.currentTextChanged.connect(self.on_history_selected)
        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_combo, 1)
        
        # 将历史记录添加到目标搜索框
        target_layout.addLayout(search_input_layout)
        target_layout.addLayout(history_layout)
        search_layout.addWidget(target_frame)
        
        # 结果显示区域
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.StyledPanel)
        result_frame.setStyleSheet("background: #f6f8fa; border-radius: 10px; padding: 15px;")
        result_layout = QVBoxLayout(result_frame)
        
        # 结果标题与操作按钮
        result_header = QHBoxLayout()
        result_title = QLabel("Search Results")
        result_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2060a0;")
        
        # 功能按钮区
        btn_layout = QHBoxLayout()
        self.detail_btn = QPushButton("Quantum Search Details")
        self.detail_btn.setObjectName("quantumDetailBtn")  # 为按钮设置对象名，用于应用特定样式
        self.detail_btn.setToolTip("View detailed information about Grover quantum search algorithm")
        self.detail_btn.clicked.connect(self.show_grover_detail)
        
        self.compare_btn = QPushButton("Algorithm Efficiency Comparison")
        self.compare_btn.setToolTip("Compare the efficiency difference between classical search and quantum search")
        self.compare_btn.clicked.connect(self.show_algorithm_comparison)
        
        export_btn = QPushButton("Export Results")
        export_btn.setToolTip("Export search results to file")
        export_btn.clicked.connect(self.export_results)
        
        settings_btn = QPushButton("Search Settings")
        settings_btn.setToolTip("Configure search parameters")
        settings_btn.clicked.connect(self.show_settings)
        
        btn_layout.addWidget(self.detail_btn)
        btn_layout.addWidget(self.compare_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(settings_btn)
        
        result_header.addWidget(result_title)
        result_header.addStretch(1)
        result_header.addLayout(btn_layout)
        
        # 结果文本显示
        self.result_text = QTextBrowser()
        self.result_text.setReadOnly(True)
        self.result_text.setOpenExternalLinks(False)  # 禁止控件内部打开链接
        self.result_text.setOpenLinks(False)  # 禁止控件内部跳转，完全由anchorClicked处理
        self.result_text.anchorClicked.connect(self.open_url)
        
        result_layout.addLayout(result_header)
        result_layout.addWidget(self.result_text)
        search_layout.addWidget(result_frame)
        
        # 标签页2: 数据库查看
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)
        db_layout.setContentsMargins(15, 20, 15, 15)
        
        db_title = QLabel("Database Content")
        db_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2060a0;")
        db_layout.addWidget(db_title)
        
        self.db_view = QTextBrowser()
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_database_view)
        
        db_layout.addWidget(self.db_view)
        db_layout.addWidget(refresh_btn)
        
        # 标签页3: 关于
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(15, 20, 15, 15)
        
        about_content = QTextBrowser()
        about_content.setHtml("""
            <h2 style="color:#2060a0;">About Grover Quantum Search System</h2>
            <p>This system combines Grover search algorithm from quantum computing with classical web crawling technology to implement a complete information retrieval solution.</p>
            <h3>Core Functions</h3>
            <ul>
                <li>Multi-source web crawler: Automatically fetches and aggregates results from multiple search engines</li>
                <li>Classical search: Traditional linear search algorithm implementation</li>
                <li>Quantum search: Grover quantum search algorithm implemented based on Qiskit</li>
                <li>Search visualization: Provides quantum circuit visualization and measurement result display</li>
                <li>Local database: Efficiently stores and manages crawled results</li>
            </ul>
            <h3>Technology Stack</h3>
            <ul>
                <li>PyQt5: Desktop GUI interface</li>
                <li>Qiskit: IBM quantum computing framework</li>
                <li>Matplotlib: Data visualization</li>
                <li>Requests/BeautifulSoup: Web crawler</li>
            </ul>
            <p>Version: 1.0.0</p>
            <p>© 2025 Grover Quantum Search Project Team</p>
        """)
        
        about_layout.addWidget(about_content)
        
        # 添加标签页到标签容器
        self.tab_widget.addTab(search_tab, "Search & Crawl")
        self.tab_widget.addTab(db_tab, "Database")
        self.tab_widget.addTab(about_tab, "About")
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建状态栏
        self.statusBar().showMessage("Ready")
        
        # 设置中央窗口部件
        self.setCentralWidget(central_widget)
        
        # 初始刷新数据库视图
        self.refresh_database_view()

    def update_statusbar(self):
        """更新状态栏信息"""
        all_data = self.db.all()
        count = len(all_data) if all_data else 0
        self.statusBar().showMessage(f"Database Records: {count} | Ready")

    def refresh_database_view(self):
        """刷新数据库视图内容"""
        all_data = self.db.all()
        if not all_data:
            self.db_view.setPlainText("Database is empty, please crawl data first!")
            return
        
        html = "<h3>Database Content (Total {0} records)</h3>".format(len(all_data))
        for i, item in enumerate(all_data, 1):
            title = item.get('title', 'No Title')
            url = item.get('url', '')
            summary = item.get('summary', 'No Summary')
            
            html += f"<p><b>{i}. {title}</b><br>"
            if url:
                html += f"URL: <a href='{url}'>{url}</a><br>"
            html += f"Summary: {summary}</p><hr>"
        
        self.db_view.setHtml(html)
        self.update_statusbar()

    def on_crawl(self):
        keyword = self.keyword_edit.text().strip()

        if not keyword:
            QMessageBox.warning(self, "Tip", "Please enter a keyword!")
            return
        
        # 网络爬取（多源）
        self.crawl_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.result_text.clear()
        self.result_text.append("<span style='color:#2060a0; font-weight:bold;'>Crawling (Bing+Baidu+Sogou), please wait...</span>")
        QApplication.processEvents()
        
        self.crawl_thread = CrawlThread(keyword)
        self.crawl_thread.finished.connect(self.on_crawl_finished)
        self.crawl_thread.progress.connect(self.update_progress)
        self.crawl_thread.start()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def on_crawl_finished(self, data):
        if not data:
            self.result_text.append("<span style='color:red; font-weight:bold;'>未抓取到任何数据！</span>")
        else:
            agg_data = aggregate_and_deduplicate(data)
            self.db.add_items(agg_data)
            self.result_text.append(f"<span style='color:green; font-weight:bold;'>抓取成功！已存储{len(agg_data)}条去重后的数据。</span>")
            # 刷新数据库视图
            self.refresh_database_view()
        
        self.crawl_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.update_statusbar()

    def on_search(self):
        target = self.target_edit.text().strip()
        self.result_text.clear()  # 先清空结果显示区
        
        if not target:
            QMessageBox.warning(self, "提示", "请输入要查找的目标！")
            return
            
        alg = self.alg_combo.currentText()
        all_data = self.db.all()
        
        if not all_data:
            QMessageBox.warning(self, "提示", "数据库为空，请先抓取数据！")
            return
            
        # 显示搜索中状态
        self.result_text.append(f"<span style='color:#2060a0; font-weight:bold;'>正在使用{alg}搜索\"{target}\"...</span>")
        QApplication.processEvents()
        
        # 记录开始时间，用于性能比较
        start_time = time.time()
        
        if "经典" in alg:  # 修改判断条件，更稳健的方式检查是否为经典搜索
            # 支持模糊匹配：只要目标作为子串出现在标题或摘要即可
            matched = [item for item in all_data if target in item.get('title', '') or target in item.get('summary', '')]
            
            if matched:
                self.result_text.append(f"<span style='color:green; font-weight:bold;'>找到{len(matched)}条匹配结果：</span>")
                
                for idx, item in enumerate(matched, 1):
                    url = item.get('url','')
                    title = item.get('title','')
                    summary = item.get('summary', '')
                    
                    # 自动还原/link?url=xxx类型URL
                    real_url = url
                    if url and url.startswith('/link?url='):
                        parsed = urllib.parse.urlparse(url)
                        query = urllib.parse.parse_qs(parsed.query)
                        url_param = query.get('url', [''])[0]
                        if url_param and (url_param.startswith('http') or url_param.startswith('https')):
                            real_url = url_param
                        else:
                            real_url = ''
                            
                    url_q = QUrl.fromUserInput(real_url) if real_url else None
                    
                    # 构建美观的HTML结果卡片
                    html = f"<div style='margin:10px 0; padding:10px; border-left:4px solid #2060a0; background:#f0f7ff;'>"
                    html += f"<div style='font-size:16px; font-weight:bold;'>{idx}. {title}</div>"
                    
                    if summary:
                        html += f"<div style='margin:5px 0; color:#444;'>{summary}</div>"
                        
                    if url_q and url_q.isValid() and real_url:
                        html += f"<div style='color:#666;'>URL：<a href=\"{url_q.toString()}\" style='color:#2060a0;'>{url_q.toString()}</a></div>"
                    else:
                        html += f"<div style='color:red;'>该链接不可直接访问</div>"
                        
                    html += "</div>"
                    self.result_text.append(html)
            else:
                self.result_text.append(f"<span style='color:orange; font-weight:bold;'>未找到包含\"{target}\"的信息！</span>")
            
            # 记录搜索结束时间，计算用时
            search_time = time.time() - start_time
            self.result_text.append(f"<div style='color:#666; text-align:right;'>经典搜索耗时: {search_time:.6f}秒</div>")
            
            # 保存搜索性能数据，用于算法效率对比
            self.last_search_perf = {
                "algorithm": "classical",
                "time": search_time,
                "target": target,
                "database_size": len(all_data),
                "results_count": len(matched) if matched else 0
            }
        else:  # 量子搜索
            # 先做模糊筛选，再量子搜索
            candidates = [item for item in all_data if target in item.get('title', '')]
            
            # Grover参数校验
            if not candidates:
                self.result_text.append("<span style='color:orange; font-weight:bold;'>没有包含该关键字的候选项，无法量子搜索！</span>")
                return
                
            if any(not item.get('title', '').strip() for item in candidates):
                self.result_text.append("<span style='color:red; font-weight:bold;'>候选项存在空标题，无法量子搜索！</span>")
                return
                
            try:
                # 获取设置中的参数
                shots = getattr(self, 'setting_shots', None)
                shots_value = shots.value() if shots else 1024
                
                # 执行Grover搜索
                found, counts = grover_search([item.get('title', '') for item in candidates], target, shots=shots_value)
                
                self.result_text.append("<span style='font-weight:bold; color:#2060a0;'>Grover量子搜索测量分布：</span>")
                self.result_text.append(f"<span style='color:#666;'>量子模拟次数: {shots_value} | 候选项数量: {len(candidates)}</span>")
                
                # 创建结果表格
                total_shots = sum(counts.values())
                html_table = "<table border='0' cellspacing='0' cellpadding='5' style='width:100%; margin:10px 0; border-collapse:collapse;'>"
                html_table += "<tr style='background:#e0e8f5;'><th style='text-align:left;'>概率</th><th style='text-align:left;'>状态</th><th style='text-align:left;'>内容</th></tr>"
                
                # 添加表格行
                for state, cnt in sorted(counts.items(), key=lambda x: -x[1]):
                    idx = int(state, 2)
                    if idx < len(candidates):
                        candidate = candidates[idx]
                        prob = cnt / total_shots
                        title = candidate.get('title', '')
                        url = candidate.get('url', '')
                        
                        # 处理URL
                        real_url = url
                        if url and url.startswith('/link?url='):
                            parsed = urllib.parse.urlparse(url)
                            query = urllib.parse.parse_qs(parsed.query)
                            url_param = query.get('url', [''])[0]
                            if url_param and (url_param.startswith('http') or url_param.startswith('https')):
                                real_url = url_param
                            else:
                                real_url = ''
                                
                        url_q = QUrl.fromUserInput(real_url) if real_url else None
                        
                        # 根据概率设置不同的背景颜色
                        bg_color = "#e0f7e0" if prob > 0.5 else "#f0f7ff"
                        
                        html_table += f"<tr style='background:{bg_color};'>"
                        html_table += f"<td style='font-weight:bold; color:#2060a0;'>{prob:.2%}</td>"
                        html_table += f"<td>{state}</td>"
                        
                        if url_q and url_q.isValid() and real_url:
                            html_table += f"<td>{title}<br><span style='color:#666; font-size:13px;'>URL: <a href=\"{url_q.toString()}\" style='color:#2060a0;'>{url_q.toString()}</a></span></td>"
                        else:
                            html_table += f"<td>{title}<br><span style='color:red; font-size:13px;'>链接不可用</span></td>"
                            
                        html_table += "</tr>"
                
                html_table += "</table>"
                self.result_text.append(html_table)
                self.result_text.append("<div style='color:#666; font-size:13px; margin-top:10px;'>提示: 点击\"量子搜索详情\"按钮可查看量子电路和算法原理</div>")
                
            except Exception as e:
                self.result_text.append(f"<span style='color:red; font-weight:bold;'>Grover搜索异常：{str(e)}</span>")
            
            # 记录搜索结束时间，计算用时
            search_time = time.time() - start_time
            self.result_text.append(f"<div style='color:#666; text-align:right;'>量子搜索耗时: {search_time:.6f}秒</div>")
            
            # 显示量子详情按钮（可能之前被隐藏）
            self.detail_btn.setVisible(True)
            
            # 保存搜索性能数据，用于算法效率对比
            self.last_search_perf = {
                "algorithm": "quantum",
                "time": search_time,
                "target": target, 
                "database_size": len(all_data),
                "candidates_size": len(candidates),
                "shots": shots_value if 'shots_value' in locals() else 1024
            }
            
            # 提示用户可以查看量子搜索详情
            self.result_text.append("""
            <div style="margin: 15px 0; padding: 10px; background-color: #f0f7ff; border-left: 4px solid #2060a0;">
                <b>提示:</b> 点击上方"<span style="color:#2060a0">量子搜索详情</span>"按钮查看量子电路和算法原理。
            </div>
            """)
        
        # 显示算法对比按钮
        self.compare_btn.setVisible(True)
                
        # 更新历史记录
        if target:  
            self.update_search_history(target)

    def show_grover_detail(self):
        """显示Grover量子搜索算法详情"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy, QDialogButtonBox, QTabWidget
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        from grover.grover_core import create_oracle, generate_grover_circuit_image, simulate_and_plot
        import numpy as np
        from qiskit import QuantumCircuit
        
        # 获取最近一次量子搜索参数
        target = self.target_edit.text().strip()
        all_data = self.db.all()
        candidates = [item.get('title', '') for item in all_data if target in item.get('title', '')]
        
        if not candidates:
            n = 3
            target_state = [1,0,1]
            info = "（未找到候选项，展示默认3比特电路）"
        else:
            n = int(np.ceil(np.log2(len(candidates))))
            N = 2 ** n
            pad_db = list(candidates) + [None] * (N - len(candidates))
            try:
                idx = pad_db.index(target)
            except ValueError:
                idx = 0  # fallback
            target_state = [int(x) for x in bin(idx)[2:].zfill(n)]
            info = f"（当前候选数：{len(candidates)}，比特数：{n}，目标态：{''.join(map(str,target_state))}）"
            
        # 构建完整Grover电路
        qc = QuantumCircuit(n, n)
        qc.h(range(n))
        oracle = create_oracle(n, target_state)
        
        # 计算迭代次数
        iterations = int(np.floor(np.pi/4 * np.sqrt(2 ** n)))
        for _ in range(iterations):
            qc.append(oracle.to_gate(), range(n))
            # Diffusion
            circ = QuantumCircuit(n)
            circ.h(range(n))
            circ.x(range(n))
            circ.h(n-1)
            circ.mcx(list(range(n-1)), n-1)
            circ.h(n-1)
            circ.x(range(n))
            circ.h(range(n))
            circ.name = "Diffusion"
            qc.append(circ.to_gate(), range(n))
        qc.measure(range(n), range(n))
        
        # 创建可视化窗口
        dlg = QDialog(self)
        dlg.setWindowTitle("Grover量子搜索算法详情")
        dlg.setGeometry(200, 100, 1000, 800)
        layout = QVBoxLayout()
        
        # 创建标签页
        detail_tabs = QTabWidget()
        
        # 标签页1：电路图
        circuit_tab = QWidget()
        circuit_layout = QVBoxLayout(circuit_tab)
        
        # 算法简介
        intro = ("<div style='margin-bottom:20px;'>"
                 "<h3>Grover量子搜索算法简介</h3>"
                 "<p>Grover算法是一种用于无序数据库搜索的量子算法，能以O(√N)复杂度找到目标项，远快于经典O(N)。</p>"
                 "<p>核心流程包括Hadamard叠加、Oracle标记目标、扩散算子放大概率，最后测量得到目标。</p>"
                 f"<p><b>下图为当前量子搜索完整电路{info}</b></p>"
                 "</div>")
        intro_label = QLabel()
        intro_label.setText(intro)
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("font-size: 15px;")
        circuit_layout.addWidget(intro_label)
        
        # 绘制电路
        fig = Figure(figsize=(min(12, 2*n), 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        qc.draw(output='mpl', ax=ax)
        ax.axis('off')
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        circuit_layout.addWidget(canvas)
        
        # 标签页2：测量结果可视化
        if len(candidates) > 0:
            try:
                results_tab = QWidget()
                results_layout = QVBoxLayout(results_tab)
                
                # 执行模拟并获取图形
                shots = getattr(self, 'setting_shots', None)
                shots_value = shots.value() if shots else 1024
                
                results_layout.addWidget(QLabel(f"量子态测量结果分布 (模拟次数: {shots_value})"))
                
                # 生成量子测量结果图
                found, counts, fig = simulate_and_plot(candidates, target, shots=shots_value)
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                results_layout.addWidget(canvas)
                
                result_info = QLabel(f"搜索目标: {target}\n最可能结果: {found}\n候选数据量: {len(candidates)}")
                result_info.setStyleSheet("font-size: 15px;")
                results_layout.addWidget(result_info)
                
                detail_tabs.addTab(results_tab, "测量结果")
            except Exception as e:
                # 如果模拟失败，不添加这个标签页
                print(f"无法生成量子测量结果: {str(e)}")
        
        # 标签页3：原理解释
        theory_tab = QWidget()
        theory_layout = QVBoxLayout(theory_tab)
        
        theory_text = QTextBrowser()
        theory_text.setHtml("""
            <h3>Grover量子搜索算法原理</h3>
            
            <h4>1. 量子计算基础</h4>
            <p>量子比特（qubit）可以同时处于多个状态的叠加态，这为并行计算提供了可能性。
            n个量子比特可以表示2^n个状态的叠加，远超过经典计算的能力。</p>
            
            <h4>2. Grover算法的四个关键步骤</h4>
            <ol>
                <li><b>初始化</b>：将所有量子比特通过Hadamard门置于均匀叠加态</li>
                <li><b>Oracle操作</b>：标记目标状态，将其相位反转</li>
                <li><b>扩散变换</b>：围绕平均振幅进行反射，放大目标状态的概率幅</li>
                <li><b>测量</b>：观测量子系统，获得目标状态</li>
            </ol>
            
            <h4>3. 算法优势</h4>
            <p>在包含N个元素的无序数据库中：</p>
            <ul>
                <li>经典搜索：需要O(N)次查询</li>
                <li>Grover搜索：仅需O(√N)次查询</li>
            </ul>
            <p>这种平方级加速在大规模数据搜索中具有显著优势。</p>
            
            <h4>4. 迭代次数的确定</h4>
            <p>Grover算法的迭代次数约为π√N/4，迭代过多或过少都会降低成功概率。</p>
            
            <h4>5. 应用场景</h4>
            <p>除了搜索数据库外，Grover算法还可应用于：</p>
            <ul>
                <li>解决离散优化问题</li>
                <li>密码学中的碰撞搜索</li>
                <li>作为其他量子算法的子程序</li>
            </ul>
        """)
        
        theory_layout.addWidget(theory_text)
        
        # 添加标签页到容器
        detail_tabs.addTab(circuit_tab, "量子电路")
        detail_tabs.addTab(theory_tab, "算法原理")
        layout.addWidget(detail_tabs)
        
        # 添加对话框按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        
        dlg.setLayout(layout)
        dlg.exec_()

    def show_algorithm_comparison(self):
        """显示经典搜索与量子搜索的算法效率对比"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        import numpy as np
        
        dlg = QDialog(self)
        dlg.setWindowTitle("经典搜索与量子搜索效率对比")
        dlg.setGeometry(200, 100, 1000, 800)
        layout = QVBoxLayout()
        
        # 添加说明文字
        intro = QLabel("经典搜索与Grover量子搜索算法性能对比")
        intro.setStyleSheet("font-size: 22px; font-weight: bold; color: #2060a0; margin: 10px 0;")
        intro.setAlignment(Qt.AlignCenter)
        layout.addWidget(intro)
        
        description = QLabel("""
        <p style='font-size:15px;'>
        Grover量子搜索算法在理论上具有显著的性能优势，特别是在处理大规模无序数据库时。
        经典搜索算法的时间复杂度为O(N)，而Grover量子搜索算法的复杂度为O(√N)，这意味着随着数据库规模的增长，
        量子搜索的优势将越发明显。
        </p>
        <p style='font-size:15px;'>
        下图展示了两种算法在不同数据规模下的理论性能对比：
        </p>
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 创建理论性能对比图表
        fig1 = Figure(figsize=(10, 6))
        canvas1 = FigureCanvas(fig1)
        ax1 = fig1.add_subplot(111)
        
        # 生成数据
        n_values = np.arange(1, 100)
        classical_complexity = n_values
        quantum_complexity = np.sqrt(n_values)
        
        # 绘制复杂度曲线
        ax1.plot(n_values, classical_complexity, 'r-', label='经典搜索 O(N)', linewidth=2)
        ax1.plot(n_values, quantum_complexity, 'b-', label='量子搜索 O(√N)', linewidth=2)
        ax1.set_xlabel('数据库规模 (N)', fontsize=12)
        ax1.set_ylabel('查询次数', fontsize=12)
        ax1.set_title('搜索算法复杂度对比', fontsize=14)
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        fig1.tight_layout()
        
        layout.addWidget(canvas1)
        
        # 添加实际测试数据的分析（如果有的话）
        if hasattr(self, 'last_search_perf'):
            perf_frame = QFrame()
            perf_frame.setFrameShape(QFrame.StyledPanel)
            perf_frame.setStyleSheet("background: #f6f8fa; border-radius: 10px; padding: 15px;")
            perf_layout = QVBoxLayout(perf_frame)
            
            perf_title = QLabel("最近一次搜索性能数据")
            perf_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2060a0;")
            perf_layout.addWidget(perf_title)
            
            # 根据搜索算法类型显示不同的信息
            perf_data = ""
            if self.last_search_perf["algorithm"] == "classical":
                perf_data = f"""
                <table>
                <tr><td><b>算法类型:</b></td><td>经典线性搜索</td></tr>
                <tr><td><b>搜索目标:</b></td><td>{self.last_search_perf.get('target', 'N/A')}</td></tr>
                <tr><td><b>数据库大小:</b></td><td>{self.last_search_perf.get('database_size', 0)}条记录</td></tr>
                <tr><td><b>搜索耗时:</b></td><td>{self.last_search_perf.get('time', 0):.6f}秒</td></tr>
                <tr><td><b>找到结果:</b></td><td>{self.last_search_perf.get('results_count', 0)}条记录</td></tr>
                </table>
                <p>
                经典搜索算法需要扫描整个数据库，时间复杂度为O(N)，随着数据规模增长，执行时间呈线性增长。
                </p>
                """
            else:  # quantum
                perf_data = f"""
                <table>
                <tr><td><b>算法类型:</b></td><td>Grover量子搜索</td></tr>
                <tr><td><b>搜索目标:</b></td><td>{self.last_search_perf.get('target', 'N/A')}</td></tr>
                <tr><td><b>数据库大小:</b></td><td>{self.last_search_perf.get('database_size', 0)}条记录</td></tr>
                <tr><td><b>候选项数量:</b></td><td>{self.last_search_perf.get('candidates_size', 0)}条记录</td></tr>
                <tr><td><b>量子模拟次数:</b></td><td>{self.last_search_perf.get('shots', 1024)}</td></tr>
                <tr><td><b>搜索耗时:</b></td><td>{self.last_search_perf.get('time', 0):.6f}秒</td></tr>
                </table>
                <p>
                Grover量子搜索算法的理论复杂度为O(√N)，随着数据规模增长，执行时间呈平方根增长。
                在实际模拟环境中，由于模拟量子计算需要大量经典计算资源，运行时间可能不会体现出这种优势。
                在真实量子计算机上，这种加速效应将会更加明显。
                </p>
                """
            
            perf_info = QLabel(perf_data)
            perf_info.setWordWrap(True)
            perf_layout.addWidget(perf_info)
            
            layout.addWidget(perf_frame)
        
        # 添加结论部分
        conclusion = QLabel("""
        <p style='font-size:15px;'>
        <b>结论：</b>
        Grover量子搜索算法在理论上提供了显著的速度优势，尤其是在处理大型无序数据库时。
        在实际应用中，量子计算的硬件限制和退相干问题仍然存在，但随着量子计算技术的发展，
        这种算法优势有望在未来得到充分体现。
        目前，通过量子模拟器执行的Grover算法可能不会显示出速度优势，但它展示了量子计算的潜力。
        </p>
        """)
        conclusion.setWordWrap(True)
        layout.addWidget(conclusion)
        
        # 添加关闭按钮
        button_layout = QHBoxLayout()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dlg.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dlg.setLayout(layout)
        dlg.exec_()

    def open_url(self, url: QUrl):
        # 直接用QUrl原样字符串，支持所有http(s)和特殊格式
        url_str = url.toString()
        webbrowser.open(url_str)

    def on_history_selected(self, text):
        """处理用户从历史记录中选择项目"""
        if text:
            # 将历史记录中选择的内容填入到目标输入框
            self.target_edit.setText(text)

    def show_settings(self):
        """显示设置对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QCheckBox, QDialogButtonBox, QTabWidget
        
        dlg = QDialog(self)
        dlg.setWindowTitle("搜索设置")
        dlg.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        # 创建标签页
        settings_tabs = QTabWidget()
        
        # 标签页1：量子搜索设置
        quantum_tab = QWidget()
        form = QFormLayout(quantum_tab)
        
        # 添加设置项
        self.setting_shots = QSpinBox()
        self.setting_shots.setRange(100, 10000)
        self.setting_shots.setValue(1024)  # 默认值
        self.setting_shots.setSingleStep(100)
        form.addRow("量子模拟次数:", self.setting_shots)
        
        self.setting_auto_iter = QCheckBox("自动优化迭代次数")
        self.setting_auto_iter.setChecked(True)
        form.addRow("", self.setting_auto_iter)
        
        # 标签页2：界面设置
        ui_tab = QWidget()
        ui_layout = QFormLayout(ui_tab)
        
        theme_label = QLabel("界面主题:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题"])
        ui_layout.addRow(theme_label, self.theme_combo)
        
        font_size = QSpinBox()
        font_size.setRange(12, 20)
        font_size.setValue(15)
        font_size.setSingleStep(1)
        ui_layout.addRow("字体大小:", font_size)
        
        # 添加标签页到容器
        settings_tabs.addTab(quantum_tab, "量子搜索")
        settings_tabs.addTab(ui_tab, "界面")
        layout.addWidget(settings_tabs)
        
        # 添加确定和取消按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        
        dlg.setLayout(layout)
        if dlg.exec_() == QDialog.Accepted:
            # 应用主题设置
            if self.theme_combo.currentText() == "深色主题":
                self.setPalette(self.create_dark_palette())
            else:
                self.setPalette(self.create_light_palette())

    def export_results(self):
        """导出搜索结果"""
        if not self.result_text.toPlainText().strip():
            QMessageBox.warning(self, "导出错误", "没有可导出的结果")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "保存搜索结果", "", 
            "HTML文件 (*.html);;文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 根据选择的文件类型决定导出格式
                if file_path.endswith('.html'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # 添加基本的HTML样式
                        html_content = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="utf-8">
                            <title>Grover量子搜索结果</title>
                            <style>
                                body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }
                                h1 { color: #2060a0; }
                                .result { margin: 10px 0; padding: 10px; border-left: 4px solid #2060a0; background: #f0f7ff; }
                                .timestamp { color: #666; font-size: 14px; }
                            </style>
                        </head>
                        <body>
                            <h1>Grover量子搜索结果</h1>
                            <p class="timestamp">导出时间: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                            <div class="content">
                        """
                        html_content += self.result_text.toHtml()
                        html_content += """
                            </div>
                        </body>
                        </html>
                        """
                        f.write(html_content)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.result_text.toPlainText())
                        
                QMessageBox.information(self, "导出成功", f"结果已导出至:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"错误: {str(e)}")

    # 还需要添加更新历史记录的功能
    def update_search_history(self, query):
        """更新搜索历史下拉框"""
        current_items = [self.history_combo.itemText(i) for i in range(self.history_combo.count())]
        
        # 如果查询已存在于历史记录中，先删除它
        if query in current_items:
            index = current_items.index(query)
            self.history_combo.removeItem(index)
        
        # 将新查询添加到最前面
        self.history_combo.insertItem(0, query)
        self.history_combo.setCurrentIndex(0)
        
        # 限制历史记录数量，保持最近10条
        while self.history_combo.count() > 10:
            self.history_combo.removeItem(self.history_combo.count() - 1)
            
        # 更新提示文字
        self.history_combo.setToolTip(f"当前搜索: {query}")
        
        # 强制刷新显示(模拟点击打开再关闭)
        self.history_combo.showPopup()
        self.history_combo.hidePopup()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
