from PySide6.QtWidgets import QMainWindow, QGraphicsView
from src.ui.canvas.scene import FlowScene


class MainWindow(QMainWindow):
    """Main application window with central canvas view."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgenticFlow")
        self.setGeometry(100, 100, 800, 600)
                self.scene = FlowScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
