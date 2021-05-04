import sys
import os
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
        self.open_file_action = Qt.QAction(Qt.QIcon(os.path.join('images',
                                                                 'matt-icons_folder-blue.svg')),
                                           "Open file...", self)
        self.open_file_action.setStatusTip("Open file")
        self.open_file_action.triggered.connect(self.file_open)

        self.save_file_action = Qt.QAction(Qt.QIcon(os.path.join('images',
                                                                 'rodentia-icons_media-floppy.svg')), "Save", self)
        self.save_file_action.setStatusTip("Save current page")
        self.save_file_action.triggered.connect(self.file_save)

        self.save_as_file_action = Qt.QAction(Qt.QIcon(os.path.join('images',
                                                                    'rodentia-icons_document-save-as.svg')),
                                              "Save As...", self)
        self.save_as_file_action.setStatusTip("Save current page to specified file")
        self.save_as_file_action.triggered.connect(self.file_save_as)

        self.undo_action = Qt.QAction(Qt.QIcon(os.path.join('images', 'matt-icons_edit-undo-ltr.svg')), "Undo", self)
        self.undo_action.setStatusTip("Undo last change")
        self.undo_action.triggered.connect(self.undo)

        self.redo_action = Qt.QAction(Qt.QIcon(os.path.join('images', 'matt-icons_edit-redo.svg')), "Redo", self)
        self.redo_action.setStatusTip("Redo")
        self.redo_action.triggered.connect(self.redo)

    def _create_menubar(self):
        menu_bar = self.menuBar()
        # Creating menus using a QMenu object
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        file_menu.addAction(self.open_file_action)
        file_menu.addAction(self.save_file_action)
        file_menu.addAction(self.save_as_file_action)
        self.setMenuBar(menu_bar)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

    def _create_toolbar(self):
        icon_size = Qt.QSize(40, 40)
        file_toolbar = Qt.QToolBar("File")
        self.addToolBar(QtCore.Qt.TopToolBarArea, file_toolbar)
        file_toolbar.addAction(self.open_file_action)
        file_toolbar.addAction(self.save_file_action)
        file_toolbar.addAction(self.save_as_file_action)
        file_toolbar.setIconSize(icon_size)
        file_toolbar.setFixedHeight(60)

        edit_toolbar = Qt.QToolBar("Edit")
        edit_toolbar.setIconSize(icon_size)
        self.addToolBar(edit_toolbar)
        edit_toolbar.addAction(self.undo_action)
        edit_toolbar.addAction(self.redo_action)

    def _set_statusbar(self):
        status_bar = Qt.QStatusBar()
        self.setStatusBar(status_bar)

    def _set_vtk_working_area(self):
        self.main_frame = Qt.QFrame()
        self.layout = Qt.QHBoxLayout()
        self.main_frame.setLayout(self.layout)

        self.vtkWidget_source = QVTKRenderWindowInteractor(self.main_frame)
        self.vtkWidget_target = QVTKRenderWindowInteractor(self.main_frame)

        self.convert_layout = Qt.QVBoxLayout()

        self.target_combo = Qt.QComboBox()
        self.target_combo.setToolTip("To which format do you want to convert?")
        self.target_combo.addItem("Apple")
        self.target_combo.addItem("Pear")
        self.target_combo.addItem("Lemon")
        self.convert_layout.addWidget(self.target_combo)

        self.convert_button = Qt.QPushButton("Convert")
        self.convert_button.clicked.connect(self.draw_target)
        self.convert_layout.addWidget(self.convert_button)

        self.vtkWidget_source.GetRenderWindow().GetInteractor().Initialize()
        self.vtkWidget_target.GetRenderWindow().GetInteractor().Initialize()

        self.layout.addWidget(self.vtkWidget_source)
        self.layout.addSpacing(5)
        self.layout.addLayout(self.convert_layout)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.vtkWidget_target)

        self.setCentralWidget(self.main_frame)

    def draw_target(self):
        self.draw(self.vtkWidget_target)

    def draw_source(self):
        self.draw(self.vtkWidget_source)

    def draw(self, vtkWidget):
        if not self.current_openfile:
            return

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
            self.current_openfile, _ = Qt.QFileDialog.getOpenFileName(self, "Open file", "",
                                                                      "VTK (*.vtk);All files (*.*)")
            if not self.current_openfile:
                return
            self.draw_source()
        except Exception as e:
            self.dialog_critical(str(e))

    def file_save(self):
        if self.current_openfile is None:
            # If we do not have a path, we need to use Save As.
            return self.file_save_as()
        try:
            raise Exception("Not Implemented yet")
        except Exception as e:
            self.dialog_critical(str(e))

    def file_save_as(self):
        path, _ = Qt.QFileDialog.getSaveFileName(self, "Save file", "", "vtk(*.vtk)")

        if not path:
            # If dialog is cancelled, will return ''
            return
        try:
            raise Exception("Not Implemented yet")
        except Exception as e:
            self.dialog_critical(str(e))
        else:
            self.current_openfile = path

    def undo(self):
        try:
            raise Exception("Not Implemented yet")
        except Exception as e:
            self.dialog_critical(str(e))

    def redo(self):
        try:
            raise Exception("Not Implemented yet")
        except Exception as e:
            self.dialog_critical(str(e))


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
