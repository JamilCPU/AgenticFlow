from PySide6.QtWidgets import QGraphicsScene


class FlowScene(QGraphicsScene):
    """Empty QGraphicsScene"""
    
    def __init__(self):
        super().__init__()
