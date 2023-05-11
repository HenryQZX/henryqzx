import remi.gui as gui

class ToolBar(gui.Container):

    def __init__(self, **kwargs):
        super(ToolBar, self).__init__(**kwargs)

    def add_command(self, imagePath, callback, title):
        icon = gui.Image(imagePath, margin='30px 30px')
        icon.add_class('tool')
        icon.onclick.do(callback)
        icon.attributes['title'] = title
        self.append(icon)