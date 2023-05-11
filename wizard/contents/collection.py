from contents.instance import *
from contents.service import *
from contents.logger import log
from res.EN_CN import *


class Collection(gui.Container):
    def __init__(self, appInstance, **kwargs):
        self.appInstance = appInstance
        super(Collection, self).__init__(**kwargs)

        # load widgets
        self.add_to_collection('Button', gui.Button, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('Label', gui.Label, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute', 'margin': '0'})
        self.add_to_collection('DropDown', gui.DropDown, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('ListView', gui.ListView, 'Basic', width='30px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('TextInput', gui.TextInput, 'Basic', width='150px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('Image', gui.Image, 'Basic', width='100px', height='100px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('CheckBox', gui.CheckBox, 'Basic', width='30px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('CheckBoxLabel', gui.CheckBoxLabel, 'Basic', width='30px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('Progress', gui.Progress, 'Basic', width='30px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('SpinBox', gui.SpinBox, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('Slider', gui.Slider, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('ColorPicker', gui.ColorPicker, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('Date', gui.Date, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('Link', gui.Link, 'Basic', width='100px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})
        self.add_to_collection('FileUploader', gui.FileUploader, 'Basic', width='150px', height='30px', style={
            'top': '20px', 'left': '20px', 'position': 'absolute'})

        self.add_to_collection('hair_segmentation', Service, 'Service', image='/res:widget_hair_segmentation.png',
                               style={'padding': '17px 13px'})
        self.add_to_collection('face_detection', Service, 'Service', image='/res:widget_face_detection.png',
                               style={'padding': '17px 13px'})
        self.add_to_collection('hand_tracking', Service, 'Service', image='/res:widget_hand_tracking.png',
                               style={'padding': '17px 13px'})
        self.add_to_collection('pose_detection', Service, 'Service', image='/res:widget_pose_detection.png',
                               style={'padding': '17px 13px'})
        self.add_to_collection('objectron', Service, 'Service', image='/res:widget_objectron.png',
                               style={'padding': '17px 13px'})
        # self.add_to_collection('chip_detection', Service, 'Service', image= '/res:widget_chip_detection.png', style={'padding': '17px 13px'})

        self.add_to_collection('aid_bot', Instance, 'Instance', properties={'speed': 92, 'check_connection': False},
                               image='/res:widget_aid_bot.png',
                               style={'width': '100%', 'height': '100%', 'background-color': '#282828',
                                      'opacity': '50%'})

        from cvs import OpencvVideoWidget
        self.add_to_collection('Camera', OpencvVideoWidget, 'Basic', style={
                                      'width': '200px', 'height':'300px', 'top': '20px', 'left': '20px', 'position': 'absolute'})

    def add_to_collection(self, widgetName, widgetClass, group, **kwargs_to_widget):
        if group not in self.children.keys():
            self.append(CollectionGroup(group), group)

        item = GroupItem(self.appInstance, widgetName, widgetClass, **kwargs_to_widget)
        self.children[group].append(item)


class CollectionGroup(gui.VBox):

    def __init__(self, title):
        super(CollectionGroup, self).__init__()
        self.container = gui.VBox(width="100%", style={'align-items': 'flex-start', 'justify-content': 'center'})
        self.opened = True
        self.title = gui.HBox(
            style={'width': '100%', 'height': '70px', 'align-items': 'center', 'justify-content': 'center',
                   'background-color': '#383838'})
        label = gui.Label(CN_widget[title], style={'color': '#ffffff'})
        self.indicator = gui.Image('/res:collapse.png')
        self.title.append([label, self.indicator])
        self.title.onclick.do(self.openClose)
        super(CollectionGroup, self).append(self.title)
        super(CollectionGroup, self).append(self.container)

    def openClose(self, widget):
        self.opened = not self.opened
        self.indicator.set_image('/res:collapse.png') if self.opened else self.indicator.set_image('/res:expand.png')
        self.container.css_display = 'flex' if self.opened else 'none'

    def append(self, widget):
        return self.container.append(widget)


class GroupItem(gui.VBox):
    def __init__(self, appInstance, widgetName, widgetClass, **kwargs_to_widget):
        self.appInstance = appInstance
        self.widgetName = widgetName
        self.kwargs_to_widget = kwargs_to_widget
        self.widgetClass = widgetClass
        super(GroupItem, self).__init__()
        self.onclick.do(self.create_instance)
        self.style.update({'width': "100%", "height": "103px", "justify-content": "center", "align-items": "center"})
        icon_file = '/res:widget_%s.png' % self.widgetName
        icon = gui.Image(icon_file)
        label = gui.Label(varname_CN(self.widgetName), style={'font-size': '12px', 'color': '#ffffff'})
        self.append([icon, label])

    def build_widget_name_list_from_tree(self, node):
        if hasattr(node, 'variable_name') and node.variable_name is not None:
            self.varname_list.append(node.variable_name)
        for child in node.children.values():
            if type(child) != str:
                self.build_widget_name_list_from_tree(child)

    # this function will be triggered when to add new widget
    def create_instance(self, widget):
        log('-----create_instance--------')
        self.varname_list = []
        self.build_widget_name_list_from_tree(self.appInstance.project)

        variable_name = ''
        if self.widgetClass.__name__ == 'Service' or self.widgetClass.__name__ == 'Instance':
            variable_name = self.widgetName
            if variable_name in self.varname_list:
                return
        else:
            for i in range(0, 1000):
                variable_name = self.widgetName + '_' + str(i)
                if variable_name not in self.varname_list:
                    break

        try:
            widget = self.widgetClass(**self.kwargs_to_widget)
        except:
            widget = self.widgetClass(self.appInstance, **self.kwargs_to_widget)

        widget.variable_name = variable_name
        root = self.appInstance.project.children['root']
        service = root.children['service_container']
        parent = service if self.widgetClass.__name__ == 'Service' else root
        self.appInstance.add_widget_to_editor(widget, parent)
