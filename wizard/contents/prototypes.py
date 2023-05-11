#main program code prototype
proto_code_program = """
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'/home/wizard/cv/')
%(imports)s

services = %(services)s
%(code_classes)s

if __name__ == "__main__":
    %(execution)s
    %(service_execution)s
"""

#here the prototype of the main class
proto_code_main_class = """
class %(classname)s(App):
    def __init__(self, *args, **kwargs):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        super(%(classname)s, self).__init__(*args)

    def idle(self):
        #idle function called every update cycle
        %(idle)s
    
    def main(self):
        return %(classname)s.construct_ui(self)
        
    @staticmethod
    def construct_ui(self):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        %(ui_code)s
        return self.%(mainwidgetname)s
        
    %(code_event_function)s
"""

proto_widget_construction = "self.%(varname)s = %(classname)s(%(self)s)\n        "

proto_widget_style = """self.%(varname)s.style.update(%(style_dict)s)\n        """

proto_widget_text = """self.%(varname)s.set_text("%(widget_text)s")\n        """

proto_widget_varname = """self.%(varname)s.variable_name = '%(varname)s'\n        """

proto_append = "self.%(parentname)s.append(self.%(varname)s)\n        "

proto_attribute_setup = """self.%(varname)s.attributes.update({%(attr_dict)s})\n        """

proto_property_setup = """self.%(varname)s.%(property)s = %(value)s\n        """

proto_set_listener = "%(sourcename)s.%(register_function)s.do(%(listenername)s.%(listener_function)s)\n        "

proto_set_event_handler = """self.%(varname)s.%(event)s.do(self.%(handler)s)\n        """

proto_code_event_function = "def %(funcname)s(self, *args):\n        pass\n\n    "

proto_service_process = """
    camid=1
    cvs.setCustomUI()
    cap=cvs.VideoCapture(camid)
    while True:
    
        frame=cap.read()
        if frame is None:
            continue
        if camid==1:
            frame=cvs.flip(frame,1)
    
        %(service_process)s
        cvs.imshow(frame)
        sleep(1)
"""

proto_instance_prop = """%(instance)s.set_%(prop_key)s(%(prop_value)s)\n    """

proto_instance_run = """
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'/home/wizard/cv/')
%(imports)s
instance = "%(instance)s"
instance_property = %(instance_property_dict)s
if __name__ == "__main__":
    %(instance_property)s
    %(instance)s.run()
"""