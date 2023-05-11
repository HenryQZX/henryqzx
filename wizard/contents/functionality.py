import remi.gui as gui
from res.EN_CN import CN_property


class Functionality(gui.VBox):

    def __init__(self, **kwargs):
        self.selectedTag = None
        super(Functionality, self).__init__(**kwargs)
        tag = gui.HBox(style={'width': '100%', 'flex': '1 0 30px'})
        prop_tag = gui.Label(CN_property['Attribute'], style={'height': '100%', 'margin':'0', 'flex': '1', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color': '#535353', 'color': '#818181'})
        prop_tag.variable_name = 'Attribute'
        prop_tag.onclick.do(self.select)
        event_tag = gui.Label(CN_property['Event'], style={'height': '100%', 'margin':'0', 'flex': '1', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color': '#535353', 'color': '#818181'})
        event_tag.variable_name = 'Event'
        event_tag.onclick.do(self.select)
        tag.append([prop_tag, event_tag])
        self.prop_container = gui.VBox(style={'width': '100%', 'height': '100%', 'background-color': '#535353', 'justify-content': 'flex-start', 'overflow': 'hidden'})
        self.event_container = gui.VBox(style={'width': '100%', 'height': '100%', 'background-color': '#535353', 'justify-content': 'flex-start', 'overflow': 'hidden'})
        self.append([tag, self.prop_container, self.event_container])
        self.select(prop_tag)

    def select(self, widget):
        if widget == self.selectedTag:
            return
        if self.selectedTag is not None:
            self.selectedTag.style.update({'background-color': '#535353', 'color': '#818181'})
        widget.style.update({'background-color': '#282828', 'color': '#ffffff'})
        self.prop_container.style['display'] = 'flex' if widget.variable_name == 'Attribute' else 'none'
        self.event_container.style['display'] = 'flex' if widget.variable_name == 'Event' else 'none'
        self.selectedTag = widget