import remi.gui as gui
from res.EN_CN import *

class Instance(gui.VBox):
    def __init__(self, **kwargs):
        super(Instance, self).__init__(**kwargs)

    def append_item(self, node):
        item = gui.HBox(style={'width': '100%', 'height': '44px', 'justify-content': 'space-between', 'align-items': 'center', 'color': '#ffffff', 'border-bottom': '1px solid #282828'})
        item.instance = node
        # title = gui.Label(varname_CN(node.variable_name), style={'margin-left': '18px'})
        title = gui.Label(node.variable_name, style={'margin-left': '18px'})
        item.append(title, 'label')
        if node.__class__.__name__ != 'Container':
            ico = gui.Image(image='/res:instance_remove.png', style={'margin-right': '18px'})
            ico.onclick.do(self.on_item_removed, js_stop_propagation=True)
            item.append(ico)
        item.onclick.do(self.on_item_selected)
        self.append(item)

    def select(self, selected):
        for child in self.children.values():
            if child.instance.variable_name == selected.variable_name:
                child.style['background-color'] = '#00486D'
            else:
                child.style['background-color'] = '#535353'

    @gui.decorate_event
    def on_item_selected(self, item):
        return (item.instance, )

    @gui.decorate_event
    def on_item_removed(self, item):
        parent = item.get_parent()
        return (parent.instance, )

class QuickSelect(gui.VBox):

    def __init__(self, **kwargs):
        super(QuickSelect, self).__init__(**kwargs)
        self.title = gui.Label(CN_property['Instance'], style ={'width':'100%', 'height':'30px', 'margin':'0', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color': '#282828', 'color': '#ffffff', 'flex': 'none'})
        self.view = Instance(style={'justify-content': 'flex-start', 'width': '100%', 'overflow-y': 'scroll', 'overflow-x': 'hidden'})
        self.append([self.title, self.view])

    def update(self, project, selected):
        self.view.empty()
        root = project.children['root']
        self.view.append_item(root)
        for child in root.children.values():
            if not (hasattr(child, 'variable_name')) or child.variable_name is None:
                continue
            self.view.append_item(child)
        services = root.children.get('service_container', None)
        if services:
            for child in services.children.values():
                self.view.append_item(child)
        self.view.select(selected)
