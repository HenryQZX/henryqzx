import remi.gui as gui
from contents.property_input import *
from res.EN_CN import *

class Properties(gui.VBox):

    def __init__(self, appInstance, **kwargs):
        super(Properties, self).__init__(**kwargs)
        self.appInstance = appInstance

    def sync(self, widget):
        DRAG = ['width', 'height', 'left', 'top']
        for key in self.children.keys():
            if key == 'Container' or key == 'Widget':
                for child in self.children[key].children.values():
                    if hasattr(child, 'attributeName') and child.attributeName in DRAG:
                        child.set_value(widget.style[child.attributeName])

    def setup(self, widget):
        if widget.__class__.__name__ == 'Service':
            self.add(widget, 'Service')
            return
        if widget.__class__.__name__ == 'Instance':
            self.add(widget, 'Instance')
            return
        if widget.__class__.__name__ == 'Container':
            self.add(widget, 'Container')
        else:
            self.add(widget, 'VarName')
            self.add(widget, 'Widget')
        self.add(widget, 'Opacity')
        if widget.__class__.__name__ in ['Button', 'Label', 'Link', 'TextInput', 'CheckBoxLabel']:
            self.add(widget, 'Text')
        if widget.__class__.__name__ in ['Progress']:
            self.add(widget, 'Progress')

    def add(self, widget, keyword):
        if keyword == 'Opacity':
            container = PropertiesContainer(CN_property[keyword] + ':')
            container.append(OpacityPropertyInput(widget))
        elif keyword == 'VarName':
            container = gui.Container(style={'width': '100%', 'flex-direction': 'column',
                                             'padding-bottom': '2px', 'border-bottom': '1px solid #383838'})
            container.append(VarNamePropertyInput(self.appInstance, widget))
        elif keyword == 'Text':
            container = PropertiesContainer(CN_property[keyword] + ":")
            text_input = TextPropertyInput(widget)
            container.append([text_input, FontSizePropertyInput(widget, text_input), FontColorPropertyInput(widget, text_input)])
        elif keyword == 'Service':
            container = PropertiesContainer(varname_CN(widget.variable_name) + ':')
            infoLabel = gui.Label(varname_CN(widget.variable_name), style={'width': '100%', 'margin': '25px 0px', 'color': '#ffffff', 'font-size': '17px', 'padding-left': '17px'})
            container.append(infoLabel)
            defalut = gui.Label(CN_property['Default'], style={'display': 'flex', 'align-item': 'center', 'color': '#ffffff', 'font-size': '16px'})
            container.append(defalut)
        elif keyword == 'Progress':
            #'width': '100%', 'padding-top': '22px', 'padding-bottom': '22px', 'border-bottom': '1px solid #383838', 'color': '#ffffff'
            container = gui.Container(style={'width': '100%', 'flex-direction': 'column', 'background-color': '#535353',
                                             'padding-bottom': '2px', 'border-bottom': '1px solid #383838', 'margin': '8px 3px'})
            container.append([ProgressPropertyInput(widget, 'max'), ProgressPropertyInput(widget, 'value')])
        elif keyword == 'Container':
            container = PropertiesContainer(widget.variable_name + ':')
            container.append([NumPropertyInput(widget, 'width'), NumPropertyInput(widget, 'height'), ColorPropertyInput(widget)])
        elif keyword == 'Instance':
            container = PropertiesContainer(widget.variable_name + ':')
            widget.add_prop(container)
        else:
            container = PropertiesContainer(widget.variable_name + ':')
            container.append([NumPropertyInput(widget, 'width'), NumPropertyInput(widget, 'height'), NumPropertyInput(widget, 'left'), NumPropertyInput(widget, 'top'), ColorPropertyInput(widget)])
        self.append(container, keyword)


class PropertiesContainer(gui.VBox):

    def __init__(self, *args):
        super(PropertiesContainer, self).__init__()
        self.style.update({'width': '100%', 'padding-top': '22px', 'padding-bottom': '22px', 'border-bottom': '1px solid #383838', 'color': '#ffffff'})
        # infoLabel = gui.Label(label, style={'width': '100%', 'margin': '25px 0px', 'color': '#ffffff', 'font-size': '17px', 'padding-left': '17px'})
        # self.append(infoLabel)