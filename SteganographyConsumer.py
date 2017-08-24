import sys
from functools import partial
from os.path import splitext
from SteganographyGUI import *
from PySide.QtCore import *
from PySide.QtGui import *
from Steganography import *
from scipy.misc import *
from PIL.Image import *


class SteganographyConsumer(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(SteganographyConsumer, self).__init__(parent)
        self.Payload1_img=None
        self.Carrier1_img=None
        self.Carrier2_img=None
        self.Carrier2_filePath=None
        self.setupUi(self)



        # Get the views that are required to have the drag-and-drop enabled.
        views = [self.viewPayload1, self.viewCarrier1, self.viewCarrier2]
        accept = lambda e: e.accept()

        for view in views:
            # We need to accept the drag event to be able to accept the drop.
            view.dragEnterEvent = accept
            view.dragMoveEvent = accept
            view.dragLeaveEvent = accept

            # Assign an event handler (a method,) to be invoked when a drop is performed.
            view.dropEvent = partial(self.processDrop, view)

        # NOTE: The line above links "all" views to the same function, and passes the view as a parameter in the
        # function. You could pass more than one widget to the function by adding more parameters to the signature,
        # in case you want to bind more than one widget together. you can even pass in another function, as a parameter,
        # which might significantly reduce the size of your code. Finally, if you prefer to have a separate function
        # for each view, where the view name is, say, "someView", you will need to:
        # 1- Create a function with a definition similar: funcName(self, e)
        # 2- Assign the function to be invoked as the event handler:
        #   self.someView.dropEvent = self.funcName

        self.chkApplyCompression.stateChanged.connect(self.applyCompression)
        self.slideCompression.valueChanged.connect(self.slideChanged)
        self.chkOverride.stateChanged.connect(self.SaveEnable)
        self.btnSave.clicked.connect(self.Save)
        self.btnExtract.clicked.connect(self.Extract)
        self.btnClean.clicked.connect(self.Clean)



    def processDrop(self, view, e):
        """
        Process a drop event when it occurs on the views.
        """
        mime = e.mimeData()

        # Guard against types of drops that are not pertinent to this app.
        if not mime.hasUrls():
            return

        # Obtain the file path using the OS format.
        filePath = mime.urls()[0].toLocalFile()
        _, ext = splitext(filePath)

        if not ext == ".png":
            return

        # Now the file path is ready to be processed.
        #
        # TODO: Remove the print statement and continue the implementation using the filePath.
        #
        pixMap=QPixmap(filePath)
        scene=QGraphicsScene()
        pixItem=scene.addPixmap(pixMap)

        if view == self.viewPayload1:
            self.Payload1(pixItem,scene,filePath)
        elif view == self.viewCarrier1:
            self.Carrier1(pixItem,scene,filePath)
        else:
            self.Carrier2_filePath=filePath
            self.Carrier2(pixItem,scene,filePath)
    def Extract(self):
        carrier=Carrier(self.Carrier2_img)
        payload=carrier.extractPayload()
        if len(payload.img.shape)==3:
            image=QImage(payload.img.data,payload.img.shape[1],payload.img.shape[0],QImage.Format_RGB888)
        else:
            image=QImage(payload.img.data,payload.img.shape[1],payload.img.shape[0],QImage.Format_Indexed8)
        pixMap=QPixmap.fromImage(image)
        scene=QGraphicsScene()
        pixItem=scene.addPixmap(pixMap)
        self.viewPayload2.setScene(scene)
        self.viewPayload2.fitInView(pixItem,Qt.KeepAspectRatio)

    def Clean(self):
        carrier=Carrier(self.Carrier2_img)
        imsave(self.Carrier2_filePath,carrier.clean())
        pixMap=QPixmap(self.Carrier2_filePath)
        scene=QGraphicsScene()
        pixItem=scene.addPixmap(pixMap)
        self.Carrier2(pixItem,scene,self.Carrier2_filePath)
        self.viewPayload2.setScene(None)
    def Carrier2(self,pixItem,scene,filePath):
        self.viewCarrier2.setScene(scene)
        self.viewCarrier2.fitInView(pixItem,Qt.KeepAspectRatio)
        self.Carrier2_img=imread(filePath)
        self.lblCarrierEmpty.clear()
        self.btnClean.setEnabled(False)
        self.btnExtract.setEnabled(False)
        carrier=Carrier(self.Carrier2_img)
        if carrier.payloadExists() ==True:
            self.btnClean.setEnabled(True)
            self.btnExtract.setEnabled(True)
        else:
            self.lblCarrierEmpty.setText(">>>>Carrier Empty<<<")
    def SaveEnable(self):
        self.btnSave.setEnabled(False)
        if self.Payload1_img is not None and self.Carrier1_img is not None:
            if int(self.txtPayloadSize.text())<=int(self.txtCarrierSize.text()):
                if self.lblPayloadFound.text() != "":
                    if self.chkOverride.isChecked() ==True:
                        self.btnSave.setEnabled(True)
                else:
                    self.btnSave.setEnabled(True)
    def Save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, caption='Open XML file ...', filter="PNG files (*.png)")
        carrier=Carrier(self.Carrier1_img)
        payload=Payload(self.Payload1_img,int(self.txtCompression.text()))
        embed_carrier=carrier.embedPayload(payload,self.chkOverride.isChecked())
        imsave(filePath,embed_carrier)
    def Payload1(self,pixItem,scene,filePath):
        self.viewPayload1.setScene(scene)
        self.viewPayload1.fitInView(pixItem,Qt.KeepAspectRatio)
        self.Payload1_img=imread(filePath)
        payload=Payload(self.Payload1_img,-1)
        self.txtPayloadSize.setText(str(len(payload.xml)))
        self.chkApplyCompression.setChecked(False)
        self.lblLevel.setEnabled(False)
        self.slideCompression.setEnabled(False)
        self.txtCompression.setEnabled(False)
        self.slideCompression.setSliderPosition(0)
        self.txtCompression.setText("0")
        self.SaveEnable()
    def Carrier1(self,pixItem,scene,filePath):
        self.viewCarrier1.setScene(scene)
        self.viewCarrier1.fitInView(pixItem,Qt.KeepAspectRatio)
        self.Carrier1_img=imread(filePath)
        if len(self.Carrier1_img.shape)==3:
            Carrier1_size=int(self.Carrier1_img.shape[0]*self.Carrier1_img.shape[1]*3/8)
        else:
            Carrier1_size=int(self.Carrier1_img.shape[0]*self.Carrier1_img.shape[1]/8)
        self.txtCarrierSize.setText(str(Carrier1_size))
        self.chkOverride.setEnabled(False)
        self.lblPayloadFound.clear()
        carrier=Carrier(self.Carrier1_img)
        if carrier.payloadExists() ==True:
            self.chkOverride.setEnabled(True)
            self.lblPayloadFound.setText(">>>>Payload Found<<<")
        self.SaveEnable()
    def applyCompression(self):
        if self.chkApplyCompression.isChecked()==True:
            self.slideCompression.setEnabled(True)
            self.txtCompression.setEnabled(True)
            self.lblLevel.setEnabled(True)
            payload=Payload(self.Payload1_img,0)
            self.txtPayloadSize.setText(str(len(payload.xml)))
        else:
            self.slideCompression.setEnabled(False)
            self.txtCompression.setEnabled(False)
            self.lblLevel.setEnabled(False)
            payload=Payload(self.Payload1_img,-1)
            self.txtPayloadSize.setText(str(len(payload.xml)))
        self.SaveEnable()

    def slideChanged(self):
        self.txtCompression.setText(str(self.slideCompression.value()))
        payload=Payload(self.Payload1_img,self.slideCompression.value())
        self.txtPayloadSize.setText(str(len(payload.xml)))
        self.SaveEnable()

if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = SteganographyConsumer()
    currentForm.show()
    currentApp.exec_()