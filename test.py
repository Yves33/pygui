import os, pathlib
## force using either bundle api or classig imgui api
os.environ["IMGUI_IMPL"]="imgui-classic"
os.environ["IMGUI_IMPL"]="imgui-bundle"

import pygui
import moderngl_window as mglw
if os.environ["IMGUI_IMPL"]=="imgui-classic":
    print('using raw imgui')
    import imgui
    from moderngl_window.integrations.imgui import ModernglWindowRenderer
    ImTextureRef=lambda x:x
    BUNDLEAPI=False
else:
    print('using bundle imgui')
    from imgui_bundle import imgui
    from moderngl_window_integrations_imgui_bundle import ModernglWindowRenderer
    ImTextureRef=lambda x:imgui.ImTextureRef(x)
    BUNDLEAPI=True


import fractions
ZOOMFACTOR=fractions.Fraction(4,3)

class WindowEvents(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "imgui Integration"
    resource_dir = (pathlib.Path(__file__)).parent.resolve()
    aspect_ratio = None
    vsync=False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error
        self.impl = ModernglWindowRenderer(self.wnd)
        self.img=self.load_texture_2d("./chess.png", flip_y=False)
        self.impl.register_texture(self.img)

        ## initialize useful variables
        self.yaw=180   # phi
        self.pitch=90  # theta
        self.roll=0
        self.pos=100
        self.pos_int=100
        self.pos_float=100.0
        self.pos_fract=100.0
        self.range=(0,200)
        self.range2=(10701,15852)
        self.keyframes=[]
        self.keyframes_int=[]
        self.keyframes_float=[]
        self.keyframes_fract=[]
        self.fspath_f=pathlib.Path(__file__).parent.resolve()/"test.png"
        self.fspath_d=pathlib.Path(os.getcwd())
        self.roi=(0,0,0,0)
        self.crop_region=(0.25,0.25,0.75,0.75)
        self.polygon=[]
        self.circles=False
        self.ruler=True
        self.colored_ranges=[[0,200],[0,200],[0,200],[0,200],[0,200]]
        self.colored_ranges_enabled=[True]*len(self.colored_ranges)
        pygui.load_style("./themes/json/material_flat.json")
        ## hack over missing values in imgui.get_io()
        self._io_state={'key_shift':False,'key_ctrl':False,'key_alt':False,'mouse_delta':(0,0)}
        
    def on_render(self, time: float, frametime: float):
        self.render_ui()
        self.wnd.use()
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def render_ui(self):
        self.wnd.use()
        ## UI BUILDING
        imgui.new_frame()
        ## hack for imgui.get_io() incorrect values
        imgui.get_io().key_shift=self._io_state['key_shift']
        imgui.get_io().key_ctrl=self._io_state['key_ctrl'] 
        ## end hack
        changed=False

        ##
        ## image related functions
        ##
        imgui.begin("Test image")
        if imgui.begin_tab_bar("Images"):
            ar=self.img.width/self.img.height
            if imgui.begin_tab_item("poly")[0]:
                changed,self.polygon=pygui.image_polygon(ImTextureRef(self.img.glo),self.polygon,maxpts=5,
                                                        color=[1.0,0.,0.,1.0],fillcolor=[1.0,0.,0.,0.4],
                                                    ar=ar,thickness=2.0)
                if changed:
                    print("Polygon",self.polygon)
                imgui.end_tab_item()
            if imgui.begin_tab_item("cop")[0]:
                changed,self.crop_region=pygui.image_crop(ImTextureRef(self.img.glo),self.crop_region,
                                                    ar=ar,thickness=2.0)
                if changed:
                    print("Crop",self.crop_region)
                imgui.end_tab_item()
            if imgui.begin_tab_item("roi")[0]:
                changed,self.roi=pygui.image_roi(ImTextureRef(self.img.glo),self.roi,
                                                    ar=ar,roi_ar=None,thickness=2.0)
                if changed:
                    print("Roi",self.roi)
                imgui.end_tab_item()
            if imgui.begin_tab_item("clickable")[0]:
                clicked,(x,y)=pygui.image_clickable(ImTextureRef(self.img.glo),ar=ar, w_max=250, h_max=250)
                if clicked:
                    print("Click",x,y)
                imgui.end_tab_item()
            if imgui.begin_tab_item("expandable")[0]:
                pygui.image_expandable(ImTextureRef(self.img.glo),ar=ar, w_max=250, h_max=250)
                imgui.end_tab_item()
            if imgui.begin_tab_item("draggable")[0]:
                dragged,(x,y,w)=pygui.image_dragable(ImTextureRef(self.img.glo),ar=ar)
                if dragged:
                    print("Drag",x,y,w)
                imgui.end_tab_item()
            imgui.end_tab_bar()
        imgui.end()

        ##
        ## controls
        ##
        imgui.begin("Test_controls")
        f=pygui.file_select_button("Select file...",self.fspath_f);
        if f: print(f)
        f=pygui.file_save_as_button("Save file...  ",self.fspath_f)
        if f: print(f)
        d=pygui.dir_select_button ("Open folder...",self.fspath_d)
        if d: print(d)
        imgui.push_id("pitch_knob_id")
        self.pitch=pygui.knob_float("Pitch",self.pitch)[1]
        imgui.pop_id()
        imgui.same_line()
        imgui.push_id("yaw_knob_id")
        self.yaw=pygui.knob_float("Yaw",self.yaw)[1]
        imgui.pop_id()
        imgui.same_line()
        imgui.push_id("roll_knob_id")
        self.roll=pygui.knob_float("Roll",self.roll)[1]
        imgui.pop_id()
        if imgui.button("dump style"):
            pygui.dump_style("test_style.json",indent=4)
        imgui.end()


        ##
        ## timeline and range selection
        ##
        if BUNDLEAPI:
            imgui.begin(f"Test time_line(s)",flags=imgui.WindowFlags_.no_scrollbar|imgui.WindowFlags_.no_collapse)
        else:
            imgui.begin(f"Test time_line(s)",flags=imgui.WINDOW_NO_SCROLLBAR|imgui.WINDOW_NO_COLLAPSE)
        changed, self.circles=imgui.checkbox("Circles",self.circles)
        imgui.same_line()
        changed, self.ruler=imgui.checkbox("Ruler",self.ruler)
        if self.ruler:
            pygui.ruler("ruler",0,200)
        imgui.push_id("range_id")
        self.range=pygui.range_float2("",self.range,0,200,circles=self.circles)[1]
        imgui.pop_id()
        ## no alignment - not working for keyframes
        imgui.text("No alignment - no keyframe support")
        if self.ruler:
            pygui.ruler("ruler",*self.range)
        changed,self.pos=pygui.time_line("pos",self.pos,self.keyframes,*self.range,circles=self.circles,align=0)
        if changed:
            print(self.pos)
        ## integer aligned time line, with ruler and buttons to zoom
        imgui.text("int(2) aligned, with buttons")
        ## zoom on/ from current position, after centering
        if imgui.button("+"):
            _width=(self.range[1]-self.range[0])/2
            self.range=(int(self.pos_int-_width*fractions.Fraction(3,4)),
                        int(self.pos_int+_width*fractions.Fraction(3,4) ))    
        imgui.same_line()
        if imgui.button('-'):
            _width=(self.range[1]-self.range[0])/2
            self.range=(int(self.pos_int-(self.pos_int-self.range[0])*fractions.Fraction(4,3)),
                        int(self.pos_int+(self.range[1]-self.pos_int)*fractions.Fraction(4,3) ))    
        imgui.same_line()
        if self.ruler:
            pygui.ruler("ruler",*self.range)
        changed,self.pos_int=pygui.time_line("pos_int",self.pos_int,self.keyframes_int,*self.range, align=2, circles=self.circles)
        if changed:
            print(self.pos_int)
        imgui.text("float(0.125) aligned, no ruler")
        if self.ruler:
            pygui.ruler("ruler",*self.range)
        changed,self.pos_float=pygui.time_line("pos_float",self.pos_float,self.keyframes_float,*self.range, align=0.125, circles=self.circles)
        if changed:
            print(self.pos_float)

        imgui.text("fraction(1001/30000) aligned, zoom&pan with mouse wheel(+shift)")
        if self.ruler:
            pygui.ruler("ruler",*self.range)
        changed,self.pos_fract=pygui.time_line("pos_fract",self.pos_fract,self.keyframes_fract,*self.range, align=fractions.Fraction(1001,30000), circles=self.circles)
        if changed:
            print(self.pos_fract)
        changed,self.range=pygui.pan_and_zoom(self.range,factor=fractions.Fraction(4,3),bounds=(0,200),pan=self._io_state['key_shift'])
        
        ## stacked range selectors
        imgui.new_line()
        imgui.new_line()
        pygui.ruler("dummy_ruler",0,200)
        imgui.set_cursor_pos_y(imgui.get_cursor_pos()[1]+40)
        for e in range(len(self.colored_ranges)):    
            imgui.set_cursor_pos_y(imgui.get_cursor_pos()[1]-8)
            imgui.push_id(f"range{e}")
            if BUNDLEAPI:
                col_=imgui.ImColor.hsv(e/len(self.colored_ranges),0.6,0.6)
            else:
                col_=imgui.color_convert_hsv_to_rgb(e/len(self.colored_ranges),0.6,0.6)
            changed, self.colored_ranges[e] = pygui.range_float2(f"range{e}",self.colored_ranges[e],0,200,
                                                                  circles=self.circles, 
                                                                  color=(col_[0],col_[1],col_[2],1.0),
                                                                  height_px=6,
                                                                  active=True or self.colored_ranges_enabled[e])
            if imgui.is_item_clicked():
                self.colored_ranges_enabled=[_==e for _ in range(len(self.colored_ranges_enabled))]
            imgui.pop_id()
        imgui.end()
        imgui.begin("Info")
        imgui.checkbox("Using Bundle API",BUNDLEAPI)
        imgui.end()
        # if BUNDLEAPI:
        #     imgui.show_demo_window()
        # else:
        #     imgui.show_test_window()
        # imgui.show_style_editor()
        imgui.end_frame()

    def on_resize(self, width: int, height: int):
        self.impl.resize(width, height)

    def on_key_event(self, key, action, modifiers):
        self.impl.key_event(key, action, modifiers)
        ## seems some events are ignored by imgui!
        keys = self.wnd.keys
        if key in [keys.LEFT_SHIFT,keys.RIGHT_SHIFT]:
            self._io_state['key_shift']=(action=='ACTION_PRESS')
        elif key==keys.LEFT_CTRL:
            self._io_state['key_ctrl']=(action=='ACTION_PRESS')

    def on_mouse_position_event(self, x, y, dx, dy):
        self.impl.mouse_position_event(x, y, dx, dy)
        ## seems some events are ignored by imgui!
        self._io_state['mouse_delta']=(dx,dy)

    def on_mouse_drag_event(self, x, y, dx, dy):
        self.impl.mouse_drag_event(x, y, dx, dy)

    def on_mouse_scroll_event(self, x_offset, y_offset):
        self.impl.mouse_scroll_event(x_offset, y_offset)

    def on_mouse_press_event(self, x, y, button):
        self.impl.mouse_press_event(x, y, button)

    def on_mouse_release_event(self, x: int, y: int, button: int):
        self.impl.mouse_release_event(x, y, button)

    def on_unicode_char_entered(self, char):
        self.impl.unicode_char_entered(char)

mglw.run_window_config(WindowEvents)
