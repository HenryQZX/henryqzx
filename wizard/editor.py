"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import inspect
import os
import traceback

import remi.gui as gui
import remi.server
from remi import start, App

import editor_widgets
from contents import prototypes, dialog, draggable, collection, toolbar, quick_select, properties, service, \
    functionality, instance
from contents.logger import log

if remi.server.pyLessThan3:
    import imp


    def load_source(filename):
        return imp.load_source('project', filename)
else:
    import importlib.machinery
    import importlib.util


    def load_source(filename):
        loader = importlib.machinery.SourceFileLoader('project', filename)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        _module = importlib.util.module_from_spec(spec)
        loader.exec_module(_module)
        return _module


class Project(gui.Container):
    """ The editor project is pure html with specific tag attributes
        This class loads and save the project file, 
        and also compiles a project in python code.
    """

    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)
        self.variable_name = 'App'
        self.style.update({'position': 'relative',
                           'overflow': 'auto',
                           'background-color': '#282828'})
        self.attr_editor_newclass = True

    def load(self, ifile):
        self.ifile = ifile

        _module = load_source(self.ifile)

        if hasattr(_module, 'instance'):
            return (_module.instance, _module.instance_property)

        # finding App class
        clsmembers = inspect.getmembers(_module, inspect.isclass)

        app_init_fnc = None
        for (name, value) in clsmembers:
            if issubclass(value, App) and name != 'App':
                app_init_fnc = value

        if app_init_fnc == None:
            return None

        root_widget = app_init_fnc.construct_ui(self)
        services = _module.services
        return (root_widget, services)

    def save(self, save_path_filename):
        classname = save_path_filename.split('/')[-1].split('.')[0]
        root = self.children['root']

        for child in root.children.values():
            if child.__class__.__name__ == 'Instance':
                self.save_instance(child, save_path_filename)
                return

        ui_code = self.save_ui_widget(root)
        modules_to_import = ['remi', 'remi.gui', 'cvs']  # fundamental packages
        videoWidgets = []
        services = []

        for child in root.children.values():
            if child.__class__.__name__ == 'OpencvVideoWidget':
                videoWidgets.append(child.variable_name)
        for child in root.children['service_container'].children.values():
            modules_to_import.append(child.variable_name)
            services.append(child.variable_name)

        idle = ''.join(["self." + widgetName + '.update()\n        ' for widgetName in videoWidgets]) if len(
            videoWidgets) else 'pass'
        if len(services):
            execution = "initcv(startcv, %(classname)s)" % {'classname': classname}
        else:
            # execution = "startcv(%(classname)s)" % {'classname': classname}
            execution = '''
    sio.emit('request_open_window', {
        'data': {'url': 'http://0.0.0.0:' + str(iport), 'title': '%(classname)s', 'icon': '', 'camid': 0}})
    start(%(classname)s, update_interval=0.03, address='0.0.0.0', port=iport, start_browser=False, enable_file_cache=False)''' % {
                'classname': classname}
        service_execution = prototypes.proto_service_process % {'service_process': ''.join(
            ["frame=" + service + ".process(frame)\n        " for service in services])} if len(services) else ''

        event_code = self.save_event_handler(root)
        code_class = prototypes.proto_code_main_class % {'classname': classname,
                                                         'ui_code': ui_code,
                                                         'mainwidgetname': self.children['root'].variable_name,
                                                         'idle': idle,
                                                         'code_event_function': event_code if len(event_code) else ''}

        compiled_code = prototypes.proto_code_program % {
            'imports': '\n'.join(["from " + modulename + " import *" for modulename in modules_to_import]),
            'code_classes': code_class,
            'services': services,
            'classname': classname,
            'execution': execution,
            'service_execution': service_execution}

        f = open(save_path_filename, "w")
        f.write(compiled_code)
        f.close()

    def save_event_handler(self, widget):
        ret_code = ''
        widgetVarName = widget.variable_name
        classname = widget.__class__.__name__

        if classname == 'Service':
            return ret_code

        # here get the event handler function definition
        if hasattr(widget, "eventHandler"):
            for handler in widget.eventHandler.values():
                #     def %(funcname)s%(parameters)s:\n        pass\n\n
                ret_code += prototypes.proto_code_event_function % {'funcname': handler}
        log(ret_code)

        for child in widget.children.values():
            if not (hasattr(child, 'variable_name')) or child.variable_name is None:
                continue
            child_code = self.save_event_handler(child)
            if child_code != '':
                ret_code += child_code
        return ret_code

    def save_ui_widget(self, widget):
        ret_code = ''
        widgetVarName = widget.variable_name
        classname = widget.__class__.__name__

        if classname == 'Service':
            return ret_code

        ret_code += prototypes.proto_widget_construction % {'varname': widgetVarName, 'classname': classname,
                                                            'self': 'self'} if classname == 'OpencvVideoWidget' else prototypes.proto_widget_construction % {
            'varname': widgetVarName, 'classname': classname, 'self': ''}
        ret_code += prototypes.proto_widget_style % {'varname': widgetVarName, 'style_dict': widget.style}
        ret_code += prototypes.proto_widget_varname % {'varname': widgetVarName}
        ret_code += prototypes.proto_widget_text % {'varname': widgetVarName,
                                                    'widget_text': widget.get_text()} if widget.__class__.__name__ in [
            'Button', 'Label', 'Link'] else ''

        # here append set event handler for each widget
        if hasattr(widget, "eventHandler"):
            for event, handler in widget.eventHandler.items():
                # self.%(varname)s.%(event)s.do(self.%(handler)s)
                ret_code += prototypes.proto_set_event_handler % {'varname': widgetVarName, 'event': event,
                                                                  'handler': handler}

        for child in widget.children.values():
            if not (hasattr(child, 'variable_name')) or child.variable_name is None:
                continue
            child_code = self.save_ui_widget(child)
            if child_code != '':
                ret_code += child_code
                ret_code += prototypes.proto_append % {'parentname': widgetVarName, 'varname': child.variable_name}
        return ret_code

    def save_instance(self, widget, save_path_filename):
        instance_prop = ''
        for prop_key in widget.properties.keys():
            instance_prop += prototypes.proto_instance_prop % {'instance': widget.variable_name, 'prop_key': prop_key,
                                                               'prop_value': widget.properties[prop_key]}
        compiled_code = prototypes.proto_instance_run % {'imports': 'from ' + widget.variable_name + ' import *',
                                                         'instance': widget.variable_name,
                                                         'instance_property': instance_prop,
                                                         'instance_property_dict': widget.properties}
        f = open(save_path_filename, "w")
        f.write(compiled_code)
        f.close()


class Editor(App):

    def __init__(self, *args):
        editor_res_path = os.path.join(os.path.dirname(__file__), 'res')
        self.drag_helpers = []
        super(Editor, self).__init__(
            *args, static_file_path={'res': editor_res_path})

    def idle(self):
        # pass
        for drag_helper in self.drag_helpers:
            drag_helper.update_position()

    def main(self):
        self.mainContainer = gui.Container(
            style={'width': '100%', 'height': '100%', 'min-width': '1280px', 'min-height': '720px'})

        self.services = service.Services(self)

        self.fileOpenDialog = dialog.OpenProjectDialog(self, style={'width': '100%', 'height': 'calc(100% - 87px)',
                                                                    'justify-content': 'flex-start',
                                                                    'align-items': 'center'})
        self.fileSaveDialog = dialog.SaveProjectDialog(self, style={'width': '100%', 'height': 'calc(100% - 87px)',
                                                                    'justify-content': 'flex-start',
                                                                    'align-items': 'center'})

        self.toolbar = toolbar.ToolBar(
            style={'width': '100%', 'height': '87px', 'display': 'flex', 'align-items': 'center',
                   'justify-content': 'center', 'background-color': '#383838'})
        logo = gui.Image(image='/res:logo.png', style={'position': 'absolute', 'top': '23px', 'left': '45px'})
        self.toolbar.append(logo)
        self.toolbar.add_command('/res:new.png', self.menu_new_clicked, '新建')
        self.toolbar.add_command('/res:save.png', self.menu_save_clicked, '保存')
        self.toolbar.add_command('/res:saveas.png', self.fileSaveDialog.show_dialog, '另存为')
        self.toolbar.add_command('/res:open.png', self.fileOpenDialog.show_dialog, '打开文件')
        self.toolbar.add_command('/res:delete.png', self.menu_delete_selection_clicked, '删除')
        self.toolbar.add_command('/res:cut.png', self.menu_cut_selection_clicked, '剪切')
        self.toolbar.add_command('/res:paste.png', self.menu_paste_selection_clicked, '粘贴')
        self.toolbar.add_command('/res:hide_widget.png', self.menu_toggle_left, '组件栏')
        self.toolbar.add_command('/res:hide_property.png', self.menu_toggle_right, '属性栏')
        self.toolbar.append(gui.Image('/res:dash.png'))
        self.toolbar.add_command('/res:source.png', self.menu_code_clicked, '源码')
        self.toolbar.add_command('/res:builder.png', self.menu_builder_clicked, '封装')

        self.mainContainer.append(self.toolbar)

        self.subContainer = gui.HBox(style={'width': '100%', 'height': 'calc(100% - 87px)'})
        self.mainContainer.append(self.subContainer, 'contents')

        self.subContainerLeft = collection.Collection(self,
                                                      style={'height': '100%', 'width': '130px', 'overflow-x': 'hidden',
                                                             'overflow-y': 'scroll', 'background-color': '#535353',
                                                             'flex': 'none'})
        self.show_left = True

        self.centralContainer = gui.VBox(style={'width': '100%', 'height': '100%'})

        self.subContainerRight = functionality.Functionality(
            style={'height': '100%', 'width': '366px', 'position': 'absolute', 'right': '0px', 'flex': 'none'})
        self.show_right = True

        self.quickSelect = quick_select.QuickSelect(
            style={'width': '100%', 'height': '242px', 'background-color': '#535353',
                   'justify-content': 'flex-start', 'flex': 'none'})
        self.quickSelect.view.on_item_selected.do(self.on_quick_select)
        self.quickSelect.view.on_item_removed.do(self.on_quick_remove)
        self.subContainerRight.append(self.quickSelect, 'quick_select')

        self.signalConnectionManager = editor_widgets.SignalConnectionManager(width='100%', style={'order': '-2'})

        self.subContainerRight.event_container.append(self.signalConnectionManager)

        self.subContainer.append(
            [self.subContainerLeft, self.centralContainer, self.subContainerRight])

        self.drag_helpers = [draggable.ResizeHelper(self, width=53, height=53),
                             draggable.DragHelper(self, width=53, height=53)]
        for drag_helper in self.drag_helpers:
            drag_helper.stop_drag.do(self.on_drag_resize_end)
            drag_helper.set_snap_grid_size(10)

        self.menu_new_clicked(None)

        return self.mainContainer

    def on_drag_resize_end(self, emitter):
        if self.elementProperties.get(self.selectedWidget.variable_name) is not None:
            self.elementProperties[self.selectedWidget.variable_name].sync(self.selectedWidget)

    def add_widget_to_editor(self, widget, parent):
        if widget.__class__.__name__ == 'OpencvVideoWidget':
            widget.set_image('/res:Camera.png')
        widget.onclick.do(self.on_widget_selection, js_stop_propagation=True, js_prevent_default=True)
        widget.attributes['draggable'] = 'true'
        key = "root" if parent == self.project else widget.identifier
        parent.append(widget, key)
        self.on_widget_selection(widget)

    def on_quick_select(self, item, selected):
        self.on_widget_selection(selected)

    def on_quick_remove(self, item, removed):
        parent = removed.get_parent()
        parent.remove_child(removed)
        todel = removed
        if self.selectedWidget == removed:
            self.on_widget_selection(self.project.children['root'])
        else:
            self.on_widget_selection(self.selectedWidget)
        del self.elementProperties[todel.variable_name]
        del todel

    def on_widget_selection(self, widget):
        self.remove_box_shadow_selected_widget()
        self.selectedWidget = widget
        if self.selectedWidget == self.project:
            return
        self.selectedWidget.style['box-shadow'] = '0 0 10px rgb(33,150,243)'

        self.signalConnectionManager.update(self.selectedWidget, self.project)

        if self.elementProperties.get(self.selectedWidget.variable_name) is None:
            self.elementProperties[self.selectedWidget.variable_name] = properties.Properties(self,
                                                                                              style={'width': '100%',
                                                                                                     'overflow-x': 'hidden',
                                                                                                     'overflow-y': 'scroll',
                                                                                                     'justify-content': 'flex-start',
                                                                                                     'order': '-2',
                                                                                                     'flex': '1 0 400px'})
            self.elementProperties[self.selectedWidget.variable_name].setup(self.selectedWidget)
        self.elementProperties[self.selectedWidget.variable_name].sync(self.selectedWidget)
        self.subContainerRight.prop_container.empty()
        self.subContainerRight.prop_container.append(self.elementProperties[self.selectedWidget.variable_name],
                                                     'properties')
        log(self.subContainerRight.prop_container.children['properties'])

        for drag_helper in self.drag_helpers:
            if self.selectedWidget == self.project:
                drag_helper.setup(None, None)
            else:
                drag_helper.setup(self.selectedWidget, self.selectedWidget.get_parent())

        self.quickSelect.update(self.project, self.selectedWidget)
        self.services.update()
        log('<<<<<<<<<<<<<<<<<<<<End: on_widget_selection<<<<<<<<<<<<<<<<<')

    def menu_new_clicked(self, Widget):
        if self.notEditMode():
            self.mainContainer.append(self.subContainer, 'contents')
        self.editCuttedWidget = None
        self.elementProperties = {}
        self.projectPathFilename = ''
        self.services = service.Services(self)
        self.project = Project(width='100%', height='100%')
        self.centralContainer.append(self.project, 'project')
        self.project.style['position'] = 'relative'
        self.selectedWidget = None
        self.on_widget_selection(self.project)
        stage = gui.Container(height='520px', width='320px',
                              style={'top': '200px', 'left': '200px', 'position': 'absolute',
                                     # 'margin': '-260px 0 0 -160px',
                                     'background-color': '#ffffff'})
        stage.variable_name = "stage"
        self.add_widget_to_editor(stage, self.project)
        stage.ondblclick.do(self.adjust_stage)
        stage.append(self.services.container, 'service_container')
        stage.append(self.services.link)

    def adjust_stage(self, widget):
        if self.notEditMode():
            return
        self.on_widget_selection(widget)

    def on_open_dialog_confirm(self, filelist):
        if len(filelist):
            self.menu_new_clicked(None)
            try:
                a, b = self.project.load(filelist[0])
                if a != None:
                    self.projectPathFilename = filelist[0]
                    root = self.project.children['root']
                    if type(a) is str:
                        image_loc = '/res:widget_%s.png' % a
                        ins = instance.Instance(b, image=image_loc,
                                                style={'width': '100%', 'height': '100%', 'background-color': '#282828',
                                                       'opacity': '50%'})
                        ins.variable_name = a
                        self.add_widget_to_editor(ins, root)
                    else:
                        root.style.update(a.style)
                        for child in a.children.values():
                            self.add_widget_to_editor(child, root)
                        for serviceName in b:
                            image_loc = '/res:widget_%s.png' % serviceName
                            myservice = service.Service(image=image_loc, style={'padding': '17px 13px'})
                            myservice.variable_name = serviceName
                            self.add_widget_to_editor(myservice, root.children['service_container'])
            except:
                errDialog = dialog.ErrorDialog(self, traceback.format_exc())
                errDialog.show_dialog()

    def menu_save_clicked(self, *args):
        if not len(self.projectPathFilename):
            self.fileSaveDialog.show_dialog()
            return
        if self.notEditMode():
            return
        self.on_widget_selection(self.project.children['root'])
        self.remove_box_shadow_selected_widget()
        self.project.save(self.projectPathFilename)

    def menu_code_clicked(self, widget):
        if not len(self.projectPathFilename):
            self.fileSaveDialog.show_dialog()
            return
        if self.notEditMode():
            return
        self.on_widget_selection(self.project.children['root'])
        self.project.save(self.projectPathFilename)
        fileurl = f'''
            var port = (window.location.hostname === '127.0.0.1' || window.location.hostname === '0.0.0.0') ? ':8900' : ':38900';
            window.location.href = 'http://' + window.location.hostname + port + '{ self.projectPathFilename }' + '~editor'
        '''
        self.execute_javascript(fileurl)

    def menu_builder_clicked(self, widget):
        if not len(self.projectPathFilename):
            self.fileSaveDialog.show_dialog()
            return
        if self.notEditMode():
            return
        self.on_widget_selection(self.project.children['root'])
        self.project.save(self.projectPathFilename)
        fileurl = "window.location.href='http://'+window.location.hostname+'" + ':8084' + "'"
        self.execute_javascript(fileurl)

    def remove_box_shadow_selected_widget(self):
        if self.selectedWidget is not None and 'box-shadow' in self.selectedWidget.style.keys():
            del self.selectedWidget.style['box-shadow']

    def menu_cut_selection_clicked(self, widget):
        if self.notEditMode():
            return
        if self.selectedWidget == self.project.children['root']:
            return
        parent = self.selectedWidget.get_parent()
        self.editCuttedWidget = self.selectedWidget
        parent.remove_child(self.selectedWidget)
        self.on_widget_selection(self.project.children['root'])

    def menu_paste_selection_clicked(self, widget):
        if self.notEditMode():
            return
        if self.editCuttedWidget != None:
            parent = self.project.children['root'].children[
                'service_container'] if self.editCuttedWidget.__class__.__name__ == 'Service' else \
                self.project.children['root']
            parent.append(self.editCuttedWidget, self.editCuttedWidget.identifier)
            self.on_widget_selection(self.editCuttedWidget)
            self.editCuttedWidget = None

    def menu_delete_selection_clicked(self, widget):
        if self.notEditMode():
            return
        if self.selectedWidget == self.project.children['root']:
            return
        parent = self.selectedWidget.get_parent()
        parent.remove_child(self.selectedWidget)
        todel = self.selectedWidget
        self.on_widget_selection(self.project.children['root'])
        del self.elementProperties[todel.variable_name]
        del todel

    def menu_toggle_left(self, widget):
        if self.notEditMode():
            return
        self.subContainerLeft.style['display'] = 'none' if self.show_left else 'block'
        self.show_left = not self.show_left

    def menu_toggle_right(self, widget):
        if self.notEditMode():
            return
        self.subContainerRight.style['display'] = 'none' if self.show_right else 'flex'
        self.show_right = not self.show_right

    def notEditMode(self):
        return self.mainContainer.children['contents'] != self.subContainer


if __name__ == "__main__":
    start(Editor, debug=False, address='0.0.0.0', port=8083,
          update_interval=0.05, multiple_instance=False, start_browser=False, enable_file_cache=True)
