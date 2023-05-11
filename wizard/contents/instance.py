import remi.gui as gui
from res.EN_CN import CN_property

class Instance(gui.Image):

    def __init__(self, properties,  **kwargs):
        super(Instance, self).__init__(**kwargs)
        self.properties = properties

    def add_prop(self, container):
        for prop_key in self.properties.keys():
            prop_value = self.properties[prop_key]
            if type(prop_value) is bool:
                container.append(BoolPropertyInput(self, prop_key, prop_value))
            else:
                container.append(NumPropertyInput(self, prop_key, prop_value))
    
class PropertyInput(gui.GridBox):

    def __init__(self, widget, prop_key):
        super(PropertyInput, self).__init__()
        self.style.update({'width': '100%', 'margin': '8.5px 0px'})
        self.targetWidget = widget
        self.prop_key = prop_key

    def update(self, widget, new_value):
        self.targetWidget.properties[self.prop_key] = new_value

class NumPropertyInput(PropertyInput):
    def __init__(self, widget, prop_key, prop_value):
        super(NumPropertyInput, self).__init__(widget, prop_key)
        label = gui.Label(CN_property[self.prop_key] + ':', style={'font-size': '16px', 'margin': '0', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})
        num_input = gui.SpinBox(prop_value, 0, 255, 1, style={'height': '28px', 'text-align': 'center'})
        num_input.onchange.do(self.update)
        self.style.update({'grid-template-columns': "5% 13% 5.5% 46%", 'grid-template-rows': "100%", 'grid-template-areas': "'. lbl . input'"})
        self.append({'lbl': label, 'input': num_input})

class BoolPropertyInput(PropertyInput):
    def __init__(self, widget, prop_key, prop_value):
        super(BoolPropertyInput, self).__init__(widget, prop_key)
        label = gui.Label(CN_property[self.prop_key] + ':', style={'font-size': '16px', 'margin': '0', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})
        checkbox = gui.CheckBox(checked=prop_value, style={'height': '28px', 'width': '28px', 'margin': '0'})
        checkbox.onchange.do(self.update)
        self.style.update({'grid-template-columns': "5% 32% 5.5% 32%", 'grid-template-rows': "100%", 'grid-template-areas': "'. lbl . input'"})
        self.append({'lbl': label, 'input': checkbox})
    
