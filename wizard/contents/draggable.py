import remi.gui as gui

class DraggableItem(gui.EventSource):
    def __init__(self, app_instance, **kwargs):
        gui.EventSource.__init__(self)
        self.app_instance = app_instance
        self.refWidget = None
        self.parent = None
        self.active = False
        self.origin_x = -1
        self.origin_y = -1
        self.snap_grid_size = 15

    def setup(self, refWidget, newParent):
        # refWidget is the target widget that will be resized
        # newParent is the container
        if self.parent:
            try:
                self.parent.remove_child(self)
            except:
                pass
        if newParent == None:
            return
        self.parent = newParent
        self.refWidget = refWidget

        try:
            self.parent.append(self)
        except:
            pass
        self.update_position()

    def start_drag(self, emitter, x, y):
        self.active = True
        self.app_instance.project.onmousemove.do(self.on_drag, js_prevent_default=True, js_stop_propagation=False)
        self.app_instance.project.onmouseup.do(self.stop_drag, js_prevent_default=True, js_stop_propagation=False)
        self.app_instance.project.onmouseleave.do(self.stop_drag, 0, 0, js_prevent_default=True, js_stop_propagation=False)
        
        self.app_instance.project.ontouchmove.do(self.on_drag, js_prevent_default=True, js_stop_propagation=False)
        self.app_instance.project.ontouchend.do(self.stop_drag, js_prevent_default=True, js_stop_propagation=False)
        self.app_instance.project.ontouchleave.do(self.stop_drag, 0, 0, js_prevent_default=True, js_stop_propagation=False)      
        
        self.origin_x = -1
        self.origin_y = -1

    @gui.decorate_event
    def stop_drag(self, emitter, x, y):
        self.active = False
        self.update_position()
        return ()

    def on_drag(self, emitter, x, y):
        pass

    def update_position(self):
        pass

    def set_snap_grid_size(self, value):
        self.snap_grid_size = value

    def round_grid(self, value):
        return int(value/self.snap_grid_size)*self.snap_grid_size


class ResizeHelper(gui.Widget, DraggableItem):

    def __init__(self, app_instance, **kwargs):
        super(ResizeHelper, self).__init__(**kwargs)
        DraggableItem.__init__(self, app_instance, **kwargs)
        self.style['float'] = 'none'
        self.style['background-image'] = "url('/res:resize.png')"
        self.style['position'] = 'absolute'
        self.style['left'] = '0px'
        self.style['top'] = '0px'
        self.onmousedown.do(self.start_drag)
        self.ontouchstart.do(self.start_drag)

    def setup(self, refWidget, newParent):
        self.style['display'] = 'none'
        if issubclass(newParent.__class__, gui.TabBox):
            return
        if issubclass(refWidget.__class__, gui.Widget) and 'left' in refWidget.style and 'top' in refWidget.style and \
                'width' in refWidget.style and 'height' in refWidget.style and refWidget.css_position=='absolute':
            DraggableItem.setup(self, refWidget, newParent)
            self.style['display'] = 'block'

    def on_drag(self, emitter, x, y):
        if self.active:
            if self.origin_x == -1:
                self.origin_x = float(x)
                self.origin_y = float(y)
                self.refWidget_origin_w = gui.from_pix(
                    self.refWidget.style['width'])
                self.refWidget_origin_h = gui.from_pix(
                    self.refWidget.style['height'])
            else:
                self.refWidget.style['width'] = gui.to_pix(self.round_grid(
                    self.refWidget_origin_w + float(x) - self.origin_x))
                self.refWidget.style['height'] = gui.to_pix(self.round_grid(
                    self.refWidget_origin_h + float(y) - self.origin_y))
                self.update_position()

    def update_position(self):
        self.style['position'] = 'absolute'
        if self.refWidget:
            if 'left' in self.refWidget.style and 'top' in self.refWidget.style:
                self.style['left'] = gui.to_pix(gui.from_pix(
                    self.refWidget.style['left']) + gui.from_pix(self.refWidget.style['width']))
                self.style['top'] = gui.to_pix(gui.from_pix(
                    self.refWidget.style['top']) + gui.from_pix(self.refWidget.style['height']))


class DragHelper(gui.Widget, DraggableItem):

    def __init__(self, app_instance, **kwargs):
        super(DragHelper, self).__init__(**kwargs)
        DraggableItem.__init__(self, app_instance, **kwargs)
        self.style['float'] = 'none'
        self.style['background-image'] = "url('/res:drag.png')"
        self.style['position'] = 'absolute'
        self.style['left'] = '0px'
        self.style['top'] = '0px'
        self.onmousedown.do(self.start_drag)
        self.ontouchstart.do(self.start_drag)

    def setup(self, refWidget, newParent):
        self.style['display'] = 'none'
        if issubclass(newParent.__class__, gui.TabBox):
            return
        if issubclass(refWidget.__class__, gui.Widget) and 'left' in refWidget.style and 'top' in refWidget.style and refWidget.css_position=='absolute':
            DraggableItem.setup(self, refWidget, newParent)
            self.style['display'] = 'block'

    def on_drag(self, emitter, x, y):
        if self.active:
            if self.origin_x == -1:
                self.origin_x = float(x)
                self.origin_y = float(y)
                self.refWidget_origin_x = gui.from_pix(
                    self.refWidget.style['left'])
                self.refWidget_origin_y = gui.from_pix(
                    self.refWidget.style['top'])
            else:
                self.refWidget.style['left'] = gui.to_pix(self.round_grid(
                    self.refWidget_origin_x + float(x) - self.origin_x))
                self.refWidget.style['top'] = gui.to_pix(self.round_grid(
                    self.refWidget_origin_y + float(y) - self.origin_y))
                self.update_position()

    def update_position(self):
        self.style['position'] = 'absolute'
        if self.refWidget:
            if 'left' in self.refWidget.style and 'top' in self.refWidget.style:
                self.style['left'] = gui.to_pix(gui.from_pix(
                    self.refWidget.style['left'])-gui.from_pix(self.style['width']))
                self.style['top'] = gui.to_pix(gui.from_pix(
                    self.refWidget.style['top'])-gui.from_pix(self.style['width']))