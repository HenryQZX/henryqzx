import remi.gui as gui

class Service(gui.Image):
    
    def __init__(self, **kwargs):
        super(Service, self).__init__(**kwargs)

class Services:
    def __init__(self, appInstance):
        self.appInstance = appInstance
        self.container = gui.VBox(style={'width':'62px', 'position':'absolute', 'top': '0px', 'align-items': 'flex-start', 'align-items': 'center', 'background-color': '#535353', 'border-radius': '10px', 'display': 'none'})
        self.link = gui.Image(image='/res:service_link.png', style={'position': 'absolute', 'top': '0px', 'display': 'none'})
        self.undraggable = False

    def update(self):
        num_services = len(self.container.children.keys())
        anchor_left = gui.from_pix(self.appInstance.project.children['root'].style['width'])
        anchor_top = (num_services * 72) / 2
        self.container.style['left'] = gui.to_pix(anchor_left + 60)
        self.link.style['left'] = gui.to_pix(anchor_left + 15)
        self.link.style['top'] = gui.to_pix(anchor_top)
        self.container.style['display'] = 'flex' if num_services != 0 else 'none'
        self.link.style['display'] = 'block' if num_services != 0 else 'none'