import sys
import vtk
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QMenu
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MainWindow(Qt.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("XLC")
        self.resize(800, 600)

        self._working_attributes()
        self._create_actions()
        self._create_menubar()
        self._create_toolbar()
        self._set_statusbar()
        self._set_vtk_working_area()

    def _working_attributes(self):
        self.current_openfile = None

    def _create_actions(self):
        self.open_file_action = Qt.QAction("Open file...", self)
        self.open_file_action.setStatusTip("Open file")
        self.open_file_action.triggered.connect(self.file_open)

    def _create_menubar(self):
        menu_bar = self.menuBar()
        # Creating menus using a QMenu object
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        file_menu.addAction(self.open_file_action)

        self.setMenuBar(menu_bar)

    def _create_toolbar(self):
        file_toolbar = Qt.QToolBar("File")
        self.addToolBar(QtCore.Qt.TopToolBarArea, file_toolbar)
        file_toolbar.addAction(self.open_file_action)

    def _set_statusbar(self):
        status_bar = Qt.QStatusBar()
        self.setStatusBar(status_bar)

    def _set_vtk_working_area(self):
        self.main_frame = Qt.QFrame()
        self.layout = Qt.QHBoxLayout()
        self.main_frame.setLayout(self.layout)

        self.vtkWidget_source = QVTKRenderWindowInteractor(self.main_frame)
        self.vtkWidget_target = QVTKRenderWindowInteractor(self.main_frame)

        self.convert_button = Qt.QPushButton("Convert to ??")
        self.convert_button.clicked.connect(self.draw_target)

        self.vtkWidget_source.GetRenderWindow().GetInteractor().Initialize()
        self.vtkWidget_target.GetRenderWindow().GetInteractor().Initialize()

        self.layout.addStretch(1)
        self.layout.addWidget(self.vtkWidget_source)
        self.layout.addStretch(1)
        self.layout.addWidget(self.convert_button)
        self.layout.addStretch(1)
        self.layout.addWidget(self.vtkWidget_target)
        self.layout.addStretch(1)

        self.setCentralWidget(self.main_frame)

    def draw_target(self):
        self.draw(self.vtkWidget_target)

    def draw_source(self):
        self.draw(self.vtkWidget_source)

    def draw(self, vtkWidget):
        reader = vtk.vtkUnstructuredGridReader()
        reader.SetFileName(self.current_openfile)
        reader.Update()

        extract_edges = vtk.vtkExtractEdges()
        extract_edges.SetInputConnection(reader.GetOutputPort())

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(extract_edges.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        ren = vtk.vtkRenderer()
        vtkWidget.GetRenderWindow().AddRenderer(ren)
        iren = vtkWidget.GetRenderWindow().GetInteractor()
        iren.Initialize()
        ren.AddActor(actor)
        ren.ResetCamera()

    def dialog_critical(self, s):
        dlg = Qt.QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(Qt.QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        try:
            self.current_openfile, _ = Qt.QFileDialog.getOpenFileName(self, "Open file", "", "VTK (*.vtk);All files (*.*)")
            if not self.current_openfile:
                return
            self.draw_source()
        except Exception as e:
            self.dialog_critical(str(e))


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

