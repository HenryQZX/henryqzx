import remi.gui as gui
from res.EN_CN import CN_dialog

class OpenProjectDialog(gui.VBox):

    def __init__(self, appInstance, **kwargs):
        self.appInstance = appInstance
        super(OpenProjectDialog, self).__init__(**kwargs)
        self.dialogTitle = gui.Label(text=CN_dialog['open_project'], style={'width': '100%', 'height': '56px', 'flex': 'none', 'font-size': '20px', 'background-color': '#00486D', 'color': '#FEFEFE', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'margin':'0', 'margin-bottom': '33px'})
        self.dialogDes = gui.Label(text=CN_dialog['open_project_des'], style={'width': '100%', 'text-align': 'center', 'color': '#383838', 'font-size': '20px', 'margin': '0', 'margin-bottom': '33px'})
        self.content = gui.VBox(style={'width': '698px', 'height': '457px', 'box-shadow': '0px 8px 32px 0px rgba(4, 0, 0, 0.21)'})
        self.fileNavi = gui.FileFolderNavigator(multiple_selection=False, selection_folder='.', allow_file_selection=True, allow_folder_selection=False)
        self.fileNavi.style.update({'width': '100%', 'height': 'calc(100% - 40px)', 'grid-template-columns': '50px auto 50px', 'grid-template-rows': '40px auto'})
        self.fileNavi.children['button_go'].set_text('Go')
        self.fileAct = gui.HBox(style={'width': '100%', 'height': '40px', 'flex': 'none', 'justify-content': 'flex-end'})
        self.dialogCancel = gui.Button(text=CN_dialog['cancel'], style={'width': '100px', 'height': '100%', 'flex': 'none', 'background-color': '#0792E3', 'font-size': '20px', 'color': '#FFFFFF', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'border': 'none', 'margin-right': '1px'})
        self.dialogCancel.onclick.do(self.cancel_dialog)
        self.dialogOK = gui.Button(text=CN_dialog['ok'], style={'width': '100px', 'height': '100%', 'flex': 'none', 'background-color': '#0792E3', 'font-size': '20px', 'color': '#FFFFFF', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'border': 'none'})
        self.dialogOK.onclick.do(self.complete_dialog)
        self.fileAct.append([self.dialogCancel, self.dialogOK])
        self.content.append([self.fileNavi, self.fileAct])
        self.append([self.dialogTitle, self.dialogDes, self.content])

    def show_dialog(self, *args):
        self.appInstance.mainContainer.append(self, 'contents')
    
    def cancel_dialog(self, *args):
        self.appInstance.mainContainer.append(self.appInstance.subContainer, 'contents')
    
    def complete_dialog(self, *args):
        self.cancel_dialog()
        self.appInstance.on_open_dialog_confirm(self.fileNavi.get_selection_list())

class SaveProjectDialog(OpenProjectDialog):

    def __init__(self, appInstance, **kwargs):
        super(SaveProjectDialog, self).__init__(appInstance, **kwargs)
        self.dialogTitle.set_text(CN_dialog['save_project'])
        self.dialogDes.set_text(CN_dialog['save_project_des'])
        self.fileInput = gui.HBox(style={'width': '100%', 'height': '40px', 'flex': 'none', 'justify-content': 'space-between'})
        self.fileInputLabel = gui.Label(text=CN_dialog['save_project_name'], style={'height': '100%', 'font-size': '20px', 'color': '#383838', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})
        self.fileInputIn = gui.TextInput(hint=CN_dialog['filename_input'], style={'flex': 'none', 'font-size': '20px', 'color': '#383838', 'text-align': 'center'})
        self.fileInputIn.set_value('untitled.py')
        self.fileInput.append([self.fileInputLabel, self.fileInputIn])
        self.content.remove_child(self.fileAct)
        self.fileNavi.style.update({'height': 'calc(100% - 80px)'})
        self.content.append([self.fileInput, self.fileAct])

    def complete_dialog(self, *args):
        self.cancel_dialog()
        self.appInstance.projectPathFilename = self.fileNavi.pathEditor.get_text() + '/' + self.fileInputIn.get_value()
        self.appInstance.menu_save_clicked()

class ErrorDialog(gui.VBox):

    def __init__(self, appInstance, message, **kwargs):
        self.appInstance = appInstance
        super(ErrorDialog, self).__init__(**kwargs)
        self.dialogTitle = gui.Label(text=CN_dialog['open_error'], style={'width': '100%', 'height': '56px', 'flex': 'none', 'font-size': '20px', 'background-color': '#ff0000', 'color': '#FEFEFE', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'margin':'0', 'margin-bottom': '33px'})
        self.dialogDes = gui.Label(text=CN_dialog['open_error_des'], style={'width': '100%', 'text-align': 'center', 'color': '#383838', 'font-size': '20px', 'margin': '0', 'margin-bottom': '33px'})
        self.errMessage = gui.Label(text=message, style={'width': '698px', 'height': '457px', 'box-shadow': '0px 8px 32px 0px rgba(4, 0, 0, 0.21)', 'white-space': 'pre'})
        self.dialogOK = gui.Button(text=CN_dialog['ok'], style={'width': '100px', 'height': '40px', 'flex': 'none', 'background-color': '#0792E3', 'font-size': '20px', 'color': '#FFFFFF', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'border': 'none'})
        self.dialogOK.onclick.do(self.close_dialog)
        self.append([self.dialogTitle, self.dialogDes, self.errMessage, self.dialogOK])

    def show_dialog(self, *args):
        self.appInstance.mainContainer.append(self, 'contents')
    
    def close_dialog(self, *args):
        self.appInstance.mainContainer.append(self.appInstance.subContainer, 'contents')
        del self