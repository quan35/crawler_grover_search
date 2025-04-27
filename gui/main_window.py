"""
主窗口界面（PyQt5实现）
支持关键词输入、网络抓取、聚合、数据库存储、经典与Grover搜索、结果可视化。
"""
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTextBrowser, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from web_crawler.aggregator import aggregate_and_deduplicate
from database import LocalDatabase
from classical_search import classical_linear_search
from grover.grover_core import grover_search

class CrawlThread(QThread):
    finished = pyqtSignal(list)
    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword
    def run(self):
        from web_crawler.multi_crawler import multi_source_crawl
        data = multi_source_crawl(self.keyword)
        self.finished.emit(data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grover量子搜索与网络聚合演示")
        self.setGeometry(300, 100, 1200, 950)
        from PyQt5.QtGui import QIcon
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pic.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.db = LocalDatabase()
        self.init_ui()

    def init_ui(self):
        # 设置全局QSS美化
        self.setStyleSheet('''
            QWidget {
                background: #f6f8fa;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 18px;
            }
            QLabel#TitleLabel {
                font-size: 26px;
                font-weight: bold;
                color: #2060a0;
                padding: 18px 0 8px 0;
                qproperty-alignment: AlignCenter;
            }
            QLineEdit {
                border: 1.5px solid #b0bfe6;
                border-radius: 7px;
                padding: 7px 10px;
                background: #fff;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #337ecc;
                background: #f0f7ff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4696e5, stop:1 #337ecc);
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 90px;
            }
            QPushButton:hover {
                background: #205eaa;
            }
            QComboBox {
                border: 1.5px solid #b0bfe6;
                border-radius: 7px;
                padding: 7px 10px;
                background: #fff;
                font-size: 16px;
            }
            QTextBrowser {
                background: #fafdff;
                border-radius: 10px;
                border: 1.5px solid #b0bfe6;
                font-size: 17px;
                padding: 12px 15px;
                color: #222;
            }
        ''')
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        # 标题
        title = QLabel("Grover量子搜索与网络聚合演示")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)
        # 关键词输入
        input_layout = QHBoxLayout()
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("请输入搜索关键词")
        self.crawl_btn = QPushButton("抓取网络内容")
        self.crawl_btn.clicked.connect(self.on_crawl)
        input_layout.addWidget(QLabel("关键词:"))
        input_layout.addWidget(self.keyword_edit)
        input_layout.addWidget(self.crawl_btn)
        main_layout.addLayout(input_layout)
        # 目标输入与搜索
        search_layout = QHBoxLayout()
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("请输入要查找的目标")
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.on_search)
        self.alg_combo = QComboBox()
        self.alg_combo.addItems(["经典搜索", "Grover量子搜索"])
        search_layout.addWidget(QLabel("目标:"))
        search_layout.addWidget(self.target_edit)
        search_layout.addWidget(self.alg_combo)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)
        # 结果显示
        self.result_text = QTextBrowser()
        self.result_text.setReadOnly(True)
        self.result_text.setOpenExternalLinks(False)  # 禁止控件内部打开链接
        self.result_text.setOpenLinks(False)  # 禁止控件内部跳转，完全由anchorClicked处理
        self.result_text.anchorClicked.connect(self.open_url)
        main_layout.addWidget(QLabel("结果输出:"))
        main_layout.addWidget(self.result_text)

        # 新增：量子搜索详情按钮
        self.detail_btn = QPushButton("量子搜索详情")
        self.detail_btn.clicked.connect(self.show_grover_detail)
        main_layout.addWidget(self.detail_btn)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def on_crawl(self):
        keyword = self.keyword_edit.text().strip()

        if not keyword:
            QMessageBox.warning(self, "提示", "请输入关键词！")
            return
        # 网络爬取（多源）
        self.crawl_btn.setEnabled(False)
        self.result_text.clear()
        self.result_text.append("正在抓取（Bing+百度+搜狗），请稍候...")
        QApplication.processEvents()
        self.crawl_thread = CrawlThread(keyword)
        self.crawl_thread.finished.connect(self.on_crawl_finished)
        self.crawl_thread.start()

    def on_crawl_finished(self, data):
        if not data:
            self.result_text.append("未抓取到任何数据！")
        else:
            agg_data = aggregate_and_deduplicate(data)
            self.db.add_items(agg_data)
            self.result_text.append(f"抓取并存储{len(agg_data)}条数据。")
        self.crawl_btn.setEnabled(True)

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
        if alg.startswith("经典"):
            # 支持模糊匹配：只要目标作为子串出现在标题或摘要即可
            matched = [item for item in all_data if target in item.get('title', '') or target in item.get('summary', '')]
            if matched:
                for idx, item in enumerate(matched):
                    url = item.get('url','')
                    title = item.get('title','')
                    from PyQt5.QtCore import QUrl
                    import urllib.parse
                    # 自动还原/link?url=xxx类型URL
                    real_url = url
                    if url.startswith('/link?url='):
                        parsed = urllib.parse.urlparse(url)
                        query = urllib.parse.parse_qs(parsed.query)
                        url_param = query.get('url', [''])[0]
                        if url_param and (url_param.startswith('http') or url_param.startswith('https')):
                            real_url = url_param
                        else:
                            real_url = ''
                    url_q = QUrl.fromUserInput(real_url) if real_url else None
                    if url_q and url_q.isValid() and real_url:
                        html = f"{title}<br>URL：<a href=\"{url_q.toString()}\">{url_q.toString()}</a>"
                    else:
                        html = f"{title}<br><span style='color:red'>该链接不可直接访问</span>"
                    self.result_text.append(html)
            else:
                self.result_text.append(f"未找到包含“{target}”的信息！")
        else:
            # 先做模糊筛选，再量子搜索
            candidates = [item for item in all_data if target in item.get('title', '')]
            # Grover参数校验
            if not target:
                self.result_text.append("请输入要查找的目标！")
                return
            if not candidates:
                self.result_text.append("没有包含该关键字的候选项，无法量子搜索！")
                return
            if any(not item.get('title', '').strip() for item in candidates):
                self.result_text.append("候选项存在空标题，无法量子搜索！")
                return
            try:
                found, counts = grover_search([item.get('title', '') for item in candidates], target)
                self.result_text.append("Grover量子搜索测量分布：")
                total_shots = sum(counts.values())
                for state, cnt in sorted(counts.items(), key=lambda x: -x[1]):
                    idx = int(state, 2)
                    if idx < len(candidates):
                        candidate = candidates[idx]
                        prob = cnt / total_shots
                        title = candidate.get('title', '')
                        url = candidate.get('url', '')
                        from PyQt5.QtCore import QUrl
                        import urllib.parse
                        real_url = url
                        if url.startswith('/link?url='):
                            parsed = urllib.parse.urlparse(url)
                            query = urllib.parse.parse_qs(parsed.query)
                            url_param = query.get('url', [''])[0]
                            if url_param and (url_param.startswith('http') or url_param.startswith('https')):
                                real_url = url_param
                            else:
                                real_url = ''
                        url_q = QUrl.fromUserInput(real_url) if real_url else None
                        if url_q and url_q.isValid() and real_url:
                            html = f"【概率：{prob:.2%}】{title}<br>URL：<a href=\"{url_q.toString()}\">{url_q.toString()}</a>"
                        else:
                            html = f"【概率：{prob:.2%}】{title}<br><span style='color:red'>该链接不可直接访问</span>"
                        self.result_text.append(html)
            except Exception as e:
                self.result_text.append(f"Grover搜索异常：{e}")

    def show_grover_detail(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        from grover.grover_core import create_oracle
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
        # 可视化窗口
        dlg = QDialog(self)
        dlg.setWindowTitle("Grover量子搜索算法简介与电路")
        layout = QVBoxLayout()
        # 算法简介
        intro = ("<b>Grover量子搜索算法简介：</b><br>"
                 "Grover算法是一种用于无序数据库搜索的量子算法，能以O(√N)复杂度找到目标项，远快于经典O(N)。<br>"
                 "核心流程包括Hadamard叠加、Oracle标记目标、扩散算子放大概率，最后测量得到目标。<br>"
                 f"<br><b>下图为当前量子搜索完整电路{info}：</b>")
        label = QLabel(intro)
        label.setWordWrap(True)
        layout.addWidget(label)
        # 绘制电路
        fig = Figure(figsize=(min(12,2*n),2))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        qc.draw(output='mpl', ax=ax)
        ax.axis('off')
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(canvas)
        dlg.setLayout(layout)
        dlg.setGeometry(300, 100, 1200, 950)
        dlg.exec_()

    def open_url(self, url: QUrl):
        # 直接用QUrl原样字符串，支持所有http(s)和特殊格式
        url_str = url.toString()
        import webbrowser
        webbrowser.open(url_str)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
