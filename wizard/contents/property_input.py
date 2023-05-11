import remi.gui as gui

from contents.logger import log
from res.EN_CN import CN_property


class PropertyInput(gui.GridBox):

    def __init__(self, widget, attributeName):
        super(PropertyInput, self).__init__()
        self.style.update({'width': '100%', 'margin': '8.5px 0px'})
        self.targetWidget = widget
        self.attributeName = attributeName


class NumPropertyInput(PropertyInput):
    def __init__(self, widget, attributeName):
        super(NumPropertyInput, self).__init__(widget, attributeName)
        label = gui.Label(CN_property[self.attributeName] + ':',
                          style={'font-size': '16px', 'margin': '0', 'display': 'flex', 'align-items': 'center',
                                 'justify-content': 'center'})
        unit = gui.Label('px', style={'font-size': '16px', 'margin': '0', 'display': 'flex', 'align-items': 'center',
                                      'justify-content': 'center'})
        self.num_input = gui.SpinBox(0, -9999, 9999, 1, style={'height': '28px', 'text-align': 'center'})
        self.num_input.onchange.do(self.update)
        self.style.update({'grid-template-columns': "5% 13% 5.5% 46% 5.5% 5%", 'grid-template-rows': "100%",
                           'grid-template-areas': "'. lbl . input . mea'"})
        self.append({'lbl': label, 'input': self.num_input, 'mea': unit})

    @gui.decorate_event
    def update(self, widget, new_value):
        new_v = gui.to_pix(new_value)
        self.targetWidget.style[self.attributeName] = new_v
        if self.targetWidget.__class__.__name__ == 'Container':
            margin_index = 0 if self.attributeName == 'height' else 3
            margins = self.targetWidget.style['margin'].split(' ')
            del margins[margin_index]
            margins.insert(margin_index, gui.to_pix(- (gui.from_pix(self.num_input.get_value())) / 2))
            self.targetWidget.style['margin'] = ' '.join(margins)

    def set_value(self, value):
        v = 0
        if value is not None:
            try:
                v = int(float(value.replace('px', '')))
            except ValueError:
                pass
        self.num_input.set_value(v)


class OpacityPropertyInput(PropertyInput):
    def __init__(self, widget):
        super(OpacityPropertyInput, self).__init__(widget, 'opacity')
        self.slide = gui.Slider(1, 0, 1, 0.01,
                                style={'background-color': '#959595', 'height': '4px', 'margin': '12px 0px'})
        self.slide.onchange.do(self.update)
        self.spin = gui.SpinBox(100, 0, 100, 1, style={'height': '28px', 'text-align': 'center'})
        self.spin.onchange.do(self.update)
        unit = gui.Label('%', style={'font-size': '16px', 'margin': '0', 'display': 'flex', 'align-items': 'center',
                                     'justify-content': 'center'})
        self.style.update({'grid-template-columns': "5% 50% 5.5% 15% 5.5% 5%", 'grid-template-rows': '100%',
                           'grid-template-areas': "'. slide . spin . mea'"})
        self.append({'slide': self.slide, 'spin': self.spin, 'mea': unit})

    @gui.decorate_event
    def update(self, widget, new_value):
        if widget.__class__.__name__ == 'Slider':
            self.spin.set_value(int(float(new_value) * 100))
            self.targetWidget.style[self.attributeName] = new_value
        else:
            self.slide.set_value(int(new_value) / 100)
            self.targetWidget.style[self.attributeName] = str(int(new_value) / 100)


class ColorPropertyInput(PropertyInput):
    def __init__(self, widget):
        super(ColorPropertyInput, self).__init__(widget, 'background-color')
        label = gui.Label(CN_property[self.attributeName] + ':',
                          style={'font-size': '16px', 'margin': '0', 'display': 'flex', 'align-items': 'center',
                                 'justify-content': 'center'})
        self.color_picker_container = gui.HBox(style={'justify-content': 'flex-start'})
        self.color_picker = gui.ColorPicker('#ffffff', style={'flex': '1 0 28px', 'height': '28px'})
        self.color_picker.onchange.do(self.picker_update)
        self.color_input = gui.TextInput(
            style={'color': '#ffffff', 'font-size': '18px', 'padding': '3.5px 0px', 'text-align': 'center'})
        self.color_input.set_text('#FFFFFF')
        self.color_input.onchange.do(self.input_update)
        self.color_picker_container.append([self.color_picker, self.color_input])
        self.style.update({'grid-template-columns': "5% 13% 5.5% 46%", 'grid-template-rows': "100%",
                           'grid-template-areas': "'. lbl . pick'"})
        self.append({'lbl': label, 'pick': self.color_picker_container})

    @gui.decorate_event
    def picker_update(self, widget, new_value):
        self.color_input.set_text(new_value.upper())
        self.targetWidget.style[self.attributeName] = new_value

    @gui.decorate_event
    def input_update(self, widget, new_value):
        self.color_picker.set_value(new_value.lower())
        self.targetWidget.style[self.attributeName] = new_value.lower()


class TextPropertyInput(gui.TextInput):

    def __init__(self, widget):
        self.targetWidget = widget
        origin_text = CN_property['Enter Text:'] if self.targetWidget.get_text() == '' else self.targetWidget.get_text()
        super(TextPropertyInput, self).__init__(hint=CN_property['Enter Text:'])
        self.style.update({'width': '100%', 'height': '150px', 'font-size': '16px'})
        self.onchange.do(self.update)

    def update(self, widget, new_value):
        self.targetWidget.set_text(new_value)


class VarNamePropertyInput(PropertyInput):
    def __init__(self, appInstance, widget):
        self.app = appInstance
        self.targetWidget = widget
        super(VarNamePropertyInput, self).__init__(widget, 'VarName')
        self.label = gui.Label(CN_property[self.attributeName] + ':',
                               style={'font-size': '16px', 'margin': '0', 'display': 'flex', 'align-items': 'center',
                                      'justify-content': 'center', 'color': '#FFFFFF'})
        self.value_input = gui.TextInput(single_line=True, hint='只支持英文字符',
                                         style={'text-align': 'start', 'background-color': '#3D3D3D',
                                                'font-size': '13px', 'color': '#FFFFFF',
                                                'height': '30px', 'line-height': '25px'})
        self.value_input.onchange.do(self.update)

        self.value_label = gui.Label(widget.variable_name,
                                     style={'text-align': 'start', 'font-size': '13px', 'height': '30px',
                                            'color': '#FFFFFF'})
        self.value_label.add_class('varname_label')
        self.value_label.onclick.do(self.change_to_input)
        self.style.update(
            {'background-color': '#535353', 'grid-template-columns': "2% 16% 5.5% 46%", 'grid-template-rows': "100%",
             'height': '28px', 'grid-template-areas': "'. lbl . vn .'"})
        # self.append({'lbl': label, 'vn': self.value_input})
        self.append({'lbl': self.label, 'vn': self.value_label})

    def change_to_input(self, widget):
        log('change to input')
        # widget.style['visibility'] = 'hidden'
        self.value_input.set_text(self.value_label.get_text())
        self.empty()
        # self.children.pop('vn')
        self.append({'lbl': self.label, 'vn': self.value_input})

    def update(self, widget, new_value):
        log('change to update new variable name')
        # if re.match('(^[a-zA-Z][a-zA-Z0-9_]*)|(^[_][a-zA-Z0-9_]+)', new_value) == None:
        #     self.errorDialog = gui.GenericDialog("Error", "Please type a valid variable name.", width=350, height=120)
        #     self.errorDialog.show(self.app)
        #     return
        log(self.app.selectedWidget.variable_name)
        log(new_value)
        if new_value == self.app.selectedWidget.variable_name:
            return
        if self.app.elementProperties.get(new_value) is None:
            log('replace to new key:' + new_value)
            self.app.elementProperties[new_value] = self.app.elementProperties.pop(
                self.app.selectedWidget.variable_name)
            self.app.selectedWidget.variable_name = new_value
            self.value_label.set_text(new_value)
        log(len(self.app.elementProperties))

        self.empty()
        self.append({'lbl': self.label, 'vn': self.value_label})

        self.app.on_widget_selection(self.app.selectedWidget)
        log('end ....................')
        # self.app.quickSelect.update(self.app, self.app.selectedWidget)

        # if new_value in self.varname_list:
        #     self.errorDialog = gui.GenericDialog("Error", "The typed variable name is already used. Please specify a new name.", width=350,height=150)
        #     self.errorDialog.show(self.appInstance)
        #     return
class ProgressPropertyInput(PropertyInput):
    def __init__(self, widget, attrname):
        # self.preview = preview
        super(ProgressPropertyInput, self).__init__(widget, attrname)
        self.style['margin'] = '0'
        label = gui.Label(CN_property[self.attributeName],
                          style={'margin': '0px', 'font-size': '16px', 'width': '100%', 'padding': '9.5px 17px', 'color': '#FFFFFF'})
        self.value_input = gui.SpinBox(100, 0, 10000, 1, style={'text-align': 'center', 'height': '28px'})
        self.value_input.onchange.do(self.update)
        self.value_input.variable_name = attrname
        self.style.update(
            {'background-color': '#535353', 'grid-template-columns': "5% 21% 4% 50% 20%", 'grid-template-rows': "100%",
             'grid-template-areas': "'. lbl . in .'"})
        self.append({'lbl': label, 'in': self.value_input})

    @gui.decorate_event
    def update(self, widget, new_value):
        self.targetWidget.attributes[widget.variable_name] = new_value

        # self.targetWidget.style[self.attributeName] = gui.to_pix(new_value)
        # self.preview.style[self.attributeName] = gui.to_pix(new_value)


class FontSizePropertyInput(PropertyInput):
    def __init__(self, widget, preview):
        self.preview = preview
        super(FontSizePropertyInput, self).__init__(widget, 'font-size')
        self.style['margin'] = '0'
        label = gui.Label(CN_property[self.attributeName],
                          style={'margin': '0px', 'font-size': '16px', 'width': '100%', 'padding': '9.5px 17px'})
        self.value_input = gui.SpinBox(16, 8, 96, 1, style={'text-align': 'center'})
        self.value_input.onchange.do(self.update)
        self.style.update(
            {'background-color': '#3D3D3D', 'grid-template-columns': "5% 21% 24% 50%", 'grid-template-rows': "100%",
             'grid-template-areas': "'. lbl . in'"})
        self.append({'lbl': label, 'in': self.value_input})

    @gui.decorate_event
    def update(self, widget, new_value):
        self.targetWidget.style[self.attributeName] = gui.to_pix(new_value)
        self.preview.style[self.attributeName] = gui.to_pix(new_value)


class FontColorPropertyInput(PropertyInput):

    def __init__(self, widget, preview):
        self.preview = preview
        super(FontColorPropertyInput, self).__init__(widget, 'color')
        self.style['margin'] = '0'
        label = gui.Label(CN_property[self.attributeName],
                          style={'margin': '0px', 'font-size': '16px', 'width': '100%', 'padding': '9.5px 17px'})
        self.value_input = gui.HBox(style={'justify-content': 'flex-start'})
        self.color_picker = gui.ColorPicker('#ffffff', style={'flex': '1 0 28px', 'height': '28px', 'padding': '6px'})
        self.color_picker.onchange.do(self.picker_update)
        self.color_input = gui.TextInput(
            style={'color': '#ffffff', 'font-size': '18px', 'padding': '9.5px 0px', 'text-align': 'center'})
        self.color_input.set_text('#FFFFFF')
        self.color_input.onchange.do(self.input_update)
        self.value_input.append([self.color_picker, self.color_input])
        self.style.update({'margin': '0px', 'background-color': '#3D3D3D', 'grid-template-columns': "5% 21% 24% 50%",
                           'grid-template-rows': "100%", 'grid-template-areas': "'. lbl . in'"})
        self.append({'lbl': label, 'in': self.value_input})

    @gui.decorate_event
    def picker_update(self, widget, new_value):
        self.color_input.set_text(new_value.upper())
        self.targetWidget.style[self.attributeName] = new_value
        self.preview.style[self.attributeName] = new_value

    @gui.decorate_event
    def input_update(self, widget, new_value):
        self.color_picker.set_value(new_value)
        self.targetWidget.style[self.attributeName] = new_value
        self.preview.style[self.attributeName] = new_value
