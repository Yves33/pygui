import os
if "IMGUI_IMPL" in os.environ and os.environ["IMGUI_IMPL"]=="imgui-classic":
    try:
        import imgui

    except:
        from imgui_bundle import imgui,ImVec2,ImVec4
else:
    try:
        from imgui_bundle import imgui,ImVec2,ImVec4
    except:
        import imgui
BUNDLEAPI='bundle' in str(imgui)
if BUNDLEAPI:
    ## a major difference in imgui and imgui-bundle api is the use of dissociated coords for imgui and ImVec* for imgui-bundle
    ## by defining a wrapper Vec2 / Vec 4, we can write *Vec2 everywhere!
    Vec2=lambda x,y:(ImVec2(x,y),)
    Vec4=lambda x,y,z,w:(ImVec4(x,y,z,w),)
    pygui_image=lambda tex,x,y,uv0,uv1:imgui.image(tex,ImVec2(x,y),uv0=ImVec2(*uv0),uv1=ImVec2(*uv1))
    pygui_is_window_focused=lambda:imgui.is_window_focused()
    pygui_get_content_region_avail=lambda:imgui.get_content_region_avail()
    pygui_push_font=lambda fnt,sz:imgui.push_font(fnt,sz)
    get_window_pos=imgui.get_window_pos
else:
    Vec2=lambda x,y:[x,y]
    Vec4=lambda x,y,z,w:[x,y,z,w]
    pygui_image=lambda tex,x,y,uv0,uv1:imgui.image(tex,x,y,uv0=uv0,uv1=uv1)
    pygui_is_window_focused=lambda:imgui.core.is_window_focused()
    pygui_get_content_region_avail=lambda:imgui.get_content_region_available()
    pygui_push_font=lambda fnt,sz:imgui.push_font(fnt)
    get_window_pos=imgui.get_window_position

import math, json, pathlib,fractions
from collections.abc import Iterable

## some colors are redundant...namely those starting with COLOR_EDIT
## colors=sorted([(imgui.__getattribute__(c),c) for c in dir(imgui) 
#                   if c.startswith('COLOR')
#                   and not c.startswith('COLOR_EDIT')
#                   and imgui.__getattribute__(c)<43])
#colors=sorted([(imgui.__getattribute__(c),c) for c in dir(imgui)  if c.startswith('COLOR') and not c.startswith('COLOR_EDIT')and imgui.__getattribute__(c)<43])
imguicolors=[
(0, 'COLOR_TEXT'), 
(1, 'COLOR_TEXT_DISABLED'), 
(2, 'COLOR_WINDOW_BACKGROUND'), 
(3, 'COLOR_CHILD_BACKGROUND'), 
(4, 'COLOR_POPUP_BACKGROUND'), 
(5, 'COLOR_BORDER'), 
(6, 'COLOR_BORDER_SHADOW'), 
(7, 'COLOR_FRAME_BACKGROUND'), 
(8, 'COLOR_FRAME_BACKGROUND_HOVERED'), 
(9, 'COLOR_FRAME_BACKGROUND_ACTIVE'), 
(10, 'COLOR_TITLE_BACKGROUND'), 
(11, 'COLOR_TITLE_BACKGROUND_ACTIVE'), 
(12, 'COLOR_TITLE_BACKGROUND_COLLAPSED'), 
(13, 'COLOR_MENUBAR_BACKGROUND'), 
(14, 'COLOR_SCROLLBAR_BACKGROUND'), 
(15, 'COLOR_SCROLLBAR_GRAB'), 
(16, 'COLOR_SCROLLBAR_GRAB_HOVERED'), 
(17, 'COLOR_SCROLLBAR_GRAB_ACTIVE'), 
(18, 'COLOR_CHECK_MARK'), 
(19, 'COLOR_SLIDER_GRAB'),
(20, 'COLOR_SLIDER_GRAB_ACTIVE'), 
(21, 'COLOR_BUTTON'), 
(22, 'COLOR_BUTTON_HOVERED'), 
(23, 'COLOR_BUTTON_ACTIVE'), 
(24, 'COLOR_HEADER'), 
(25, 'COLOR_HEADER_HOVERED'), 
(26, 'COLOR_HEADER_ACTIVE'), 
(27, 'COLOR_SEPARATOR'), 
(28, 'COLOR_SEPARATOR_HOVERED'), 
(29, 'COLOR_SEPARATOR_ACTIVE'), 
(30, 'COLOR_RESIZE_GRIP'), 
(31, 'COLOR_RESIZE_GRIP_HOVERED'), 
(32, 'COLOR_RESIZE_GRIP_ACTIVE'), 
(33, 'COLOR_PLOT_LINES'), 
(34, 'COLOR_PLOT_LINES_HOVERED'), 
(35, 'COLOR_PLOT_HISTOGRAM'), 
(36, 'COLOR_PLOT_HISTOGRAM_HOVERED'), 
(37, 'COLOR_TEXT_SELECTED_BACKGROUND'), 
(38, 'COLOR_DRAG_DROP_TARGET'), 
(39, 'COLOR_NAV_HIGHLIGHT'), 
(40, 'COLOR_NAV_WINDOWING_HIGHLIGHT'), 
(41, 'COLOR_NAV_WINDOWING_DIM_BACKGROUND'), 
(42, 'COLOR_MODAL_WINDOW_DIM_BACKGROUND')]


def pygui_dump_style(fname,**kwargs):
    '''Dumps current style as json file.

    Args:
        fname (str): The file path where the JSON style will be saved.
        **kwargs: Additional keyword arguments passed directly to `json.dump()`.
    '''
    style = imgui.get_style()
    attributes=[a for a in dir(style) if not a.startswith('__') and not callable(getattr(style, a))]
    jsonstyle={}
    for a in attributes:
        if not a.startswith('color'):
            value=style.__getattribute__(a)
            try:
                jsonstyle[a]=[value.x,value.y]
            except:
                jsonstyle[a]=value
        if BUNDLEAPI:
            jsonstyle['colors']={k:list(style.color_(v)) for v,k in imguicolors}
        else:
            jsonstyle['colors']={k:[*style.colors[v]] for v,k in imguicolors}
        with open(fname,'w') as fp:
            json.dump(jsonstyle,fp,**kwargs)

def pygui_load_style(fname,**kwargs):
    '''load a json saved style in memory

    Args:
        fname (str): The file path from which the JSON style will be loaded.
        **kwargs: Additional keyword arguments passed directly to `json.load()`.
    '''
    style = imgui.get_style()
    attributes=[a for a in dir(style) if not a.startswith('__') and not callable(getattr(style, a))]
    with open(fname,'r') as fp:
        jsonstyle=json.load(fp,**kwargs)
    for a in attributes:
        if not a.startswith('color') and a in jsonstyle.keys():
            if isinstance(jsonstyle[a], Iterable):
                if BUNDLEAPI:
                    style.__setattr__(a,ImVec2(*jsonstyle[a]))
                else:
                    style.__setattr__(a,imgui.Vec2(*jsonstyle[a]))
            else:
                style.__setattr__(a,jsonstyle[a])
        for v,k in imguicolors:
            if BUNDLEAPI:
                style.set_color_(v,ImVec4(*tuple(jsonstyle['colors'][k])))
            else:
                style.colors[v]=imgui.Vec4(*tuple(jsonstyle['colors'][k]))

def clip(x,lo,hi):
    return max(lo,min(x,hi))

def pct2(x, lo,hi):
    return (x-lo)/(hi-lo)
    
def pct4(x,y,l,t,r,b):
    return [(x-l)/(r-l),(y-t)/(b-t) ]

def ptinrect(x,y,l,t,r,b=None):
    if b is None:  ## consider r as circle radius, and l,t as center
        return l-r<x<l+r and t-r<y<t+r
    else:
        return (l<x<r if l<r else r<x<l) and (t<y<b if t<b else b<y<t)

def click_pct(btn,l,t,r,b):
    if imgui.is_mouse_clicked(btn) or imgui.is_mouse_dragging(btn):
        if ptinrect(*imgui.get_mouse_pos(),l,t,r,b):
            return pct4(*imgui.get_mouse_pos(),l,t,r,b)[0]

def click(btn,l,t,r=5,b=None):
    if b is None: ## b is None consider radius. compute rectangle
        l-=r
        t-=r
        b=t+r
        r=l+r
    if imgui.is_mouse_clicked(btn):
        return ptinrect(*imgui.get_mouse_pos(),l,t,r,b) ## actually should check for true distance
    return None

def drag(btn,l,t,r=5,b=None):
    if b is None: ## b is none consider radius. compute rectangle
        l-=r
        t-=r
        b=t+r
        r=l+r
    if imgui.is_mouse_dragging(btn):
        return ptinrect(*imgui.get_mouse_pos(),l,t,r,b) ## actually should check for true distance
    return None

def make_ticks(lo, hi, maxticks, minor_cnt=4):
    range_val = hi - lo
    if range_val == 0:
        return [], []
    raw_tick = range_val / max(1, maxticks - 1)
    exponent = math.floor(math.log10(raw_tick))
    fraction = raw_tick / (10 ** exponent)
    
    if fraction <= 1:
        nice_fraction = 1
    elif fraction <= 2:
        nice_fraction = 2
    elif fraction <= 5:
        nice_fraction = 5
    else:
        nice_fraction = 10
    
    nice_tick = nice_fraction * (10 ** exponent)
    # Adjust the first tick to start at `lo`
    first_tick = math.ceil(lo / nice_tick) * nice_tick
    if first_tick > lo:
        first_tick -= nice_tick
    
    # Generate major ticks
    major = []
    current = first_tick
    while current <= hi:
        major.append(current)
        current += nice_tick
    # Generate minor ticks
    minor = []
    increment = nice_tick / (minor_cnt + 1)
    current = first_tick
    while current <= hi:
        minor.append(current)
        current += increment
    return [M for M in major if lo<=M<=hi], [m for m in minor if lo<=m<=hi]

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

def pygui_ruler(label,lo,hi,maxticks=10,minor_cnt=4):
    """Displays a ruler from current position till the right side of window
    
    Args:
        name: ignored.
        lo, hi: ruler extrema.
        maxticks: maximum number of major ticks.
        minor_cnt: number of minor ticks per major interval
    Returns:
        None

    Usage: call immediately before pygui_time_line or pygui_range_float2 to display a ruler for the widget. The ticks are automatically computed based on the range and maxticks, and minor_cnt parameters.
    
    Notes (1): Occupies all space from current position till the right border of window.
    Notes (2): Does not change the current cursor position.
    """
    if BUNDLEAPI:
        textcolor=imgui.get_color_u32(imgui.Col_.text)
    else:
        style=imgui.get_style()
        textcolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_TEXT])
    style=imgui.get_style()
    major, minor = make_ticks(lo, hi, maxticks, minor_cnt)
    wsize=pygui_get_content_region_avail()              ## actual size of window content (after padding substraction)
    wcursor=imgui.get_cursor_pos()                      ## window coordinates of cursor (top left of next widget,including padding)
    height=imgui.get_font_size()+2*style.frame_padding.y    ## height of a standard slider 
    width=wsize.x-0*wcursor.x -2*style.frame_padding.x                       ## width of slider to fill window
    if width<10:
        return
    top=get_window_pos().y+wcursor.y                                    ## top of the bar (screen)
    left=get_window_pos().x+wcursor.x + style.frame_padding.x                          ## left of bar (screen)
    rect=[left,top,left+width, top+height]                  ## slider rect (screen). larger than what' actually drawn on screen
    draw_list = imgui.get_window_draw_list()
    for t in minor:
        x=left+width*pct2(t,lo,hi)
        if t<0:
            print()
        draw_list.add_line(*Vec2(x,top),*Vec2(x,top+height//3),textcolor)
    for t in major:
        x=left+width*pct2(t,lo,hi)
        assert (x>=left)
        draw_list.add_line(*Vec2(x,top),*Vec2(x,top+height),textcolor)
        draw_list.add_text(*Vec2(x+3,top+height//2),textcolor,f"{t:g}")

def pygui_pan_and_zoom(range,factor,pan=False):
        """Handles interaction with pygui_time_line (and potentially pygui_range_float2) to implement pan and zoom with mouse wheel.

        Args:
            range: current range (lo,hi). Used for both panning and zooming.
            factor: zoom factor. >1 to zoom in, <1 to zoom out accespts fractions.
            pan: if True, mouse wheel will pan instead of zoom (usually imgui.get_io().key_shift|key_ctrl).
        Returns:
            tuple (changed, new_range) where changed is True if range is changed, and new_range is the potentially updated range.

        Usage:
            call immediately after pygui_time_line or pygui_range_float2, and pass the same range. If user is hovering the widget and scrolls mouse wheel, the range will be updated accordingly. If shift is held, it will pan instead of zoom.
        """
        if imgui.is_item_hovered() and imgui.get_io().mouse_wheel!=0:
            if pan: ## needs hack to work
                range=(range[0]+2*imgui.get_io().mouse_wheel,
                            range[1]+2*imgui.get_io().mouse_wheel)
            else:
                padx=imgui.get_style().frame_padding.x
                _pos=fractions.Fraction(int(imgui.get_mouse_pos().x-padx-imgui.get_item_rect_min().x),int(imgui.get_item_rect_max().x-imgui.get_item_rect_min().x+2*padx))
                _pos=range[0]+_pos*(range[1]-range[0])
                increment= factor if imgui.get_io().mouse_wheel<0 else 1/factor
                range=(_pos-(_pos-range[0])*increment,
                            _pos+(range[1]-_pos)*increment )
            return True,range
        return False,range


def pygui_time_line(label,pos,keyframes,lo,hi,height_px=6,rightbtn=2, align=0,circles=True):
    """Displays a time_line widget. User can select position, set/remove jump to key positions (using specified button)

    clicking with rightbtn on cursor adds a key position.
    clicking with rightbtn on keyframe symbols removes the position from keyframe list
    clicking with on keyframe jumps to specified potition

    Args:
        label: ignored, but used by imgui to identify widget.
        pos: current position.
        keyframes: list of positions marked as key.
        lo,hi: current low and high values for widget
        height_px: controls size of handle(s) and span
        rightbtn: the button used to add or remove key positions
        align: the granularity of position. position is rounded to nearest multiple.
        circles: used circles (True) or triangles (False)
    Returns:
        tuple (changed, pos) - the keyframe list may be changed but this is not reported

    Notes: Occupies all space from current position till the right border of window
    """
    changed=False
    style=imgui.get_style()
    if BUNDLEAPI:
        barcolor=imgui.get_color_u32(imgui.Col_.frame_bg)
        ## barcolor=imgui.get_color_u32(imgui.ImVec4(1.0,0.0,0.0,1.0))
        handlecolor=imgui.get_color_u32(imgui.Col_.slider_grab)
        wori=get_window_pos()
        wsize=pygui_get_content_region_avail() #imgui.get_content_region_avail()
    else:
        barcolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_FRAME_BACKGROUND])
        handlecolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_SLIDER_GRAB])
        wori=get_window_pos()                    ## screen position of window top left
        wsize = pygui_get_content_region_avail()            #imgui.get_window_content_region_max()       ## actual size of window content (after padding substraction)
    wcursor=imgui.get_cursor_pos()                          ## window coordinates of cursor (top left of next widget,including padding)
    height=imgui.get_font_size()+2*style.frame_padding.y    ## height of a standard slider
    width=wsize.x-0*wcursor.x -2*style.frame_padding.x                       ## width of slider to fill window -style.frame_padding.x
    if width<0:
        return False,pos
    top=wori.y+wcursor.y                                ## top of the bar (screen)
    left=wori.x+wcursor.x + style.frame_padding.x                      ## left of bar (screen)
    rect=[left,top,left+width, top+height]              ## slider rect (screen). larger than what' actually drawn on screen
    ## rendering scrollbar and handle
    imgui.invisible_button(f"##{label}",*Vec2(width,height*2))   ## invisible button is required to get drag. our button is twice the std height, to preserve space for keyframes
    draw_list = imgui.get_window_draw_list()
    draw_list.add_rect_filled(*Vec2(left,top+height//2-height_px//2),*Vec2(left+width,top+height//2+height_px//2), barcolor)
    if align:
        pos=align*round(pos/align) ## was originally int(pos/align)
    xc=left+width*pct2(pos,lo,hi)
    yc=top+height//2
    if circles:
        draw_list.add_circle_filled(*Vec2(xc,yc), height//2,handlecolor, num_segments=16)
    else:
        draw_list.add_triangle_filled(*Vec2(xc,yc+height//3),
                                  *Vec2(xc+height//3,yc-height//3),
                                  *Vec2(xc-height//3,yc-height//3),handlecolor)
    if imgui.is_item_clicked() or (imgui.is_item_active() and imgui.is_mouse_dragging(1)):
        if pct:=click_pct(0,*rect):    ## left click. returns specified offset
            #pos=lo+round(pct*(hi-lo))
            pos=lo+ pct*(hi-lo)
            if align:
                pos=align*round(pos/align)
            changed=True
    ## right click in handle adds a keyframe
    if click(rightbtn,xc-height//2,yc-height//2,xc+height//2,yc+height//2):
        keyframes.append(pos)
    ## markers
    for f in keyframes:
        x,y=left+width*pct2(f,lo,hi),top+height*1.5
        radius=height//3
        l,t,r,b=x-radius,y-radius,x+radius,y+radius
        if click(0,l,t,r,b):
            pos=f
            changed=True
        elif click(rightbtn,l,t,r,b):
            keyframes.remove(f)
        if math.fabs(pos-f)<align/2:
            draw_list.add_circle_filled(*Vec2(x,y),radius,handlecolor, num_segments=16 if circles else 4)
        else:
            draw_list.add_circle_filled(*Vec2(x,y),radius,barcolor,num_segments=16 if circles else 4)
            draw_list.add_circle(*Vec2(x,y),radius,handlecolor,num_segments=16 if circles else 4)
    return changed,pos

@static_vars(_current=None)
def pygui_range_float2(label,bounds,v_min,v_max,height_px=6,circles=False):
    """Displays a range widget

    Args:
        label: ignored, but used by imgui to identify widget.
        bounds: low and high values of selected range (abc.collection of length 2).
        v_min,v_max: min and max values that the range can take
        height_px: controls size of handle(s) and span
        circles: used circles (True) or triangles (False)
    Returns:
        tuple (changed, (lo,hi))

    Notes: Occupies all space from current position till the right border of window
    """
    changed=False
    try:
        bounds=clip(bounds[0],v_min,v_max),clip(bounds[1],v_min,v_max)
    except:
        bounds=v_min,v_max
    style=imgui.get_style()
    if BUNDLEAPI:
        barcolor=imgui.get_color_u32(imgui.Col_.frame_bg)
        handlecolor=imgui.get_color_u32(imgui.Col_.slider_grab)
        wori=get_window_pos()
        wsize=pygui_get_content_region_avail() #imgui.get_content_region_avail()
    else:
        barcolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_FRAME_BACKGROUND])
        handlecolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_SLIDER_GRAB])
        wori=get_window_pos()                    ## screen position of window top left
        wsize = pygui_get_content_region_avail()            ## actual size of window content (after padding substraction)
    wcursor=imgui.get_cursor_pos()                          ## window coordinates of cursor (top left of next widget,including padding)
    height=imgui.get_font_size()+2*style.frame_padding.y    ## height of a standard slider
    width=wsize.x-wcursor.x -2*style.frame_padding.x                       ## width of slider to fill window
    if width<10:
        return False,bounds
    handle_span=(v_max-v_min)/width*height_px*2
    top=wori.y+wcursor.y                                    ## top of the bar (screen)
    left=wori.x+wcursor.x + style.frame_padding.x                          ## left of bar (screen)
    rect=[left,top,left+width, top+height]                  ## slider rect (screen). larger than what' actually drawn on screen
    ## rendering scrollbar and handle
    imgui.invisible_button("##range",*Vec2(width+2*style.frame_padding.x,height))    ## invisible button is required to ge drag
    draw_list = imgui.get_window_draw_list()

    draw_list.add_rect_filled(*Vec2(left,top+height//2-height_px//2),*Vec2(left+width,top+height//2+height_px//2), barcolor)
    bounds=list(bounds)
    bounds[0]=clip(bounds[0],v_min,v_max) if bounds[0] else v_min
    bounds[1]=clip(bounds[1],v_min,v_max) if bounds[1] else v_max
    lohandle=[left+width*pct2(bounds[0],v_min,v_max), top+height//2, height//2]
    hihandle=[left+width*pct2(bounds[1],v_min,v_max), top+height//2, height//2]
    if circles:
        draw_list.add_circle_filled(*Vec2(lohandle[0],lohandle[1]),lohandle[2],handlecolor)
        draw_list.add_circle_filled(*Vec2(hihandle[0],hihandle[1]),hihandle[2],handlecolor)
    else:
        draw_list.add_triangle_filled(*Vec2(lohandle[0],lohandle[1]+height//3),
                                  *Vec2(lohandle[0]+height//3,lohandle[1]-height//3),
                                  *Vec2(lohandle[0]-height//3,lohandle[1]-height//3),handlecolor)
        draw_list.add_triangle_filled(*Vec2(hihandle[0],hihandle[1]+height//3),
                                  *Vec2(hihandle[0]+height//3,hihandle[1]-height//3),
                                  *Vec2(hihandle[0]-height//3,hihandle[1]-height//3),handlecolor)
    
    centerhandle=[lohandle[0], top+height//2-height_px//2, hihandle[0],top+height//2+height_px//2]
    draw_list.add_rect_filled(*Vec2(centerhandle[0],centerhandle[1]+0),*Vec2(centerhandle[2],centerhandle[3]-0),handlecolor)
    if imgui.is_item_clicked():
        if ptinrect(*imgui.get_mouse_pos(),*lohandle):
            pygui_range_float2._current=0
        elif ptinrect(*imgui.get_mouse_pos(),*hihandle):
            pygui_range_float2._current=1
        elif ptinrect(*imgui.get_mouse_pos(),*centerhandle):
            pygui_range_float2._current=2
            p=v_min+round(click_pct(0,*rect)*(v_max-v_min))
            pygui_range_float2._drag=(p-bounds[0],p-bounds[1])
        else:
            pygui_range_float2._current=None
            pygui_range_float2._drag=(None,None)
    if imgui.is_item_active() and imgui.is_item_hovered() and imgui.is_mouse_dragging(0):
        if pygui_range_float2._current in [0,1]:
            pct=click_pct(0,*rect)
            if pct:
                bounds[pygui_range_float2._current]=v_min+round(pct*(v_max-v_min))
                ## ensure there is no collision between handles
                if pygui_range_float2._current==0:
                    bounds[0]=min(bounds[0],bounds[1]-handle_span)
                elif pygui_range_float2._current==1:
                    bounds[1]=max(bounds[1],bounds[0]+handle_span)
                changed=True
        elif pygui_range_float2._current==2:
            pct=click_pct(0,*rect)
            if pct:
                p=v_min+round(pct*(v_max-v_min))
                if 0<=p-pygui_range_float2._drag[0]<=v_max and 0<=p-pygui_range_float2._drag[1]<=v_max:
                    bounds=[p-pygui_range_float2._drag[0],p-pygui_range_float2._drag[1]]
                    changed=True
    bounds.sort()        
    return changed,(clip(bounds[0],v_min,v_max),clip(bounds[1],v_min,v_max))

def pygui_breadcrumb(p):
    for i,part in enumerate(p.parts):
        if imgui.button(part):
            #print(str(pathlib.Path(*p.parts[:i+1])))
            return True,pathlib.Path(*p.parts[:i+1])
        if i!=len(p.parts)-1:
            imgui.same_line()
    return False,p

##
## TODO: for all pygui_popup_xxx_selector
## + implement drive letter selection if on windows
## + implement combo for selecting filetype (*.mp4)
##
@static_vars(_path=None,_children=None,_invisible=False)
def pygui_popup_file_open_selector(label,path,filterlist=['[!]*'],charwidth=55,rowcount=10):
    """Displays an file selection dialog
    
    Args:
        label: label to display on top of popup window.
        path: the initial path.
        filterlist: wildcard filters for file display.
        charwidth: the width of dialog file list, in chars.
        rowcount: number of rows in dialog file list.
    Returns:
        the selected path of None if user cancelled.
    """
    self=pygui_popup_file_open_selector ## should rename to _func
    if self._path is None:
        self._path=pathlib.Path(path)
        self._item_current_idx=0
    
    if imgui.begin_popup_modal(label)[0]:
        parent=self._path.parent if self._path.is_file() else self._path
        changed,newpath=pygui_breadcrumb(parent)
        if changed:
            self._path=newpath
            self._children=None
            self._item_current_idx=0
            parent=newpath
        changed,self._invisible=imgui.checkbox("Show hidden files"+" "*(charwidth-17),self._invisible)
        imgui.separator()
        ## construct list of files
        if self._children is None or changed:
            self._children=[]
            try:
                self._children.extend([str(p.name) for p in parent.iterdir() if p.is_dir()])
                for f in filterlist:
                    self._children.extend([str(p.name) for p in parent.glob(f) if p.is_file()])
                if not self._invisible:
                    self._children=[f for f in self._children if not str(f).startswith('.')]
            except:
                ## permission error
                pass
            self._children=['..']+sorted(list(set(self._children)))

        ## display ui
        wsize=pygui_get_content_region_avail()              ## actual size of window content (after padding substraction)
        wcursor=imgui.get_cursor_pos()                      ## window coordinates of cursor (top left of next widget,including padding)
        height=imgui.get_font_size()+2*imgui.get_style().frame_padding.y    ## height of a standard slider 
        
        if BUNDLEAPI:
            if imgui.begin_list_box(f"##{label}",ImVec2(wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height))):
                for i,f in enumerate(self._children):
                    if imgui.selectable(f, self._item_current_idx == i)[0]:
                        self._item_current_idx = i
                        self._path=(parent/f).resolve()
                        self._children=None
                imgui.end_list_box()
        else:
            with imgui.begin_list_box("", wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height)) as list_box:
                if list_box.opened:
                    #imgui.listbox_header("",wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height))
                    for i,f in enumerate(self._children):
                        if imgui.selectable(f)[1]:
                            self._path=(parent/f).resolve()
                            self._children=None
                    #imgui.listbox_footer()
        imgui.separator()
        if not self._path.is_dir():
            imgui.text(self._path.name)
        else:
            imgui.text('')
        if imgui.button("Cancel"):
            imgui.close_current_popup()
            imgui.end_popup()
            return None
        imgui.same_line()
        if not self._path.is_dir() and imgui.button("Select"):
            imgui.close_current_popup()
            imgui.end_popup()
            return str(self._path)
        imgui.end_popup()
        return None

@static_vars(_path=None,_children=None,_invisible=False,_newname="Untitled.abc")
def pygui_popup_file_save_selector(label,path,filterlist=['[!]*'],charwidth=55,rowcount=10):
    """Displays an editable file selection dialog
    
    Args:
        label: label to display on top of popup window.
        path: the initial path.
        filterlist: wildcard filters for file display.
        charwidth: the width of dialog file list, in chars.
        rowcount: number of rows in dialog file list.
    Returns:
        the selected path of None if user cancelled.
    """
    self=pygui_popup_file_save_selector
    if self._path is None:
        self._path=pathlib.Path(path)
        self._item_current_idx=0

    if imgui.begin_popup_modal(label)[0]:
        parent=self._path
        changed,newpath=pygui_breadcrumb(parent)
        if changed:
            self._path=newpath
            self._children=None
            self._item_current_idx=0
            parent=newpath
        changed,self._invisible=imgui.checkbox("Show hidden files"+" "*(charwidth-17),self._invisible)
        imgui.separator()
        ## construct list of files
        if self._children is None or changed:
            self._children=[]
            try:
                self._children.extend([str(p.name) for p in parent.iterdir() if p.is_dir()])
                for f in filterlist:
                    self._children.extend([str(p.name) for p in parent.glob(f) if p.is_file()])
                if not self._invisible:
                    self._children=[f for f in self._children if not str(f).startswith('.')]
            except:
                ## permission error
                pass
            self._children=['..']+sorted(list(set(self._children)))

        ## display ui
        wsize=pygui_get_content_region_avail()              ## actual size of window content (after padding substraction)
        wcursor=imgui.get_cursor_pos()                      ## window coordinates of cursor (top left of next widget,including padding)
        height=imgui.get_font_size()+2*imgui.get_style().frame_padding.y    ## height of a standard slider
        if BUNDLEAPI:
            if imgui.begin_list_box(f"##{label}",ImVec2(wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height))):
                for i,f in enumerate(self._children):
                    if imgui.selectable(f, self._item_current_idx == i)[0]:
                        if (parent/f).resolve().is_dir():
                            self._path=(parent/f).resolve()
                            self._children=None
                        else:
                            self._item_current_idx=i
                            self._newname=f
                imgui.end_list_box()
        else:
            with imgui.begin_list_box("", wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height)) as list_box:
                if list_box.opened:
                    #imgui.listbox_header("",wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height))
                    for i,f in enumerate(self._children):
                        if imgui.selectable(f)[1]:
                            if (parent/f).resolve().is_dir():
                                self._path=(parent/f).resolve()
                                self._children=None
                            else:
                                self._newname=f
                    #imgui.listbox_footer()
        imgui.separator()
        changed,self._newname=imgui.input_text("Filename",self._newname,255)
        if imgui.button("Cancel"):
            self._newname="Untitled.abc"
            imgui.close_current_popup()
            imgui.end_popup()
            return None
        imgui.same_line()
        if len(self._newname) and imgui.button("Select"):
            imgui.close_current_popup()
            imgui.end_popup()
            return str(parent/self._newname)
        imgui.end_popup()
        return None

@static_vars(_current=0,_path=None,_children=None,_invisible=False)
def pygui_popup_dir_open_selector(label,path,charwidth=55,rowcount=10):
    """Displays a directory selection dialog
    
    Args:
        label: label to display on top of popup window.
        path: the initial path.
        charwidth: the width of dialog file list, in chars.
        rowcount: number of rows in dialog file list.
    Returns:
        the selected path of None if user cancelled.
    """
    self=pygui_popup_dir_open_selector
    if self._path is None:
        self._path=path
        self._item_current_idx=0

    ## todo add match filter / folder only
    if imgui.begin_popup_modal(label)[0]:
        parent=self._path
        changed,newpath=pygui_breadcrumb(parent)
        if changed:
            self._path=newpath
            self._children=None
            self._item_current_idx=0
            parent=newpath
        changed,self._invisible=imgui.checkbox("Show hidden files"+" "*(charwidth-17),self._invisible)
        imgui.separator()
        ## construct list of files
        if self._children is None or changed:
            self._children=[]
            try:
                self._children.extend([str(p.name) for p in parent.iterdir() if p.is_dir()])
                if not self._invisible:
                    self._children=[f for f in self._children if not str(f).startswith('.')]
            except:
                ## permission error
                pass
            self._children=['..']+sorted(list(set(self._children)))

        ## display ui
        wsize=pygui_get_content_region_avail()              ## actual size of window content (after padding substraction)
        wcursor=imgui.get_cursor_pos()                      ## window coordinates of cursor (top left of next widget,including padding)
        height=imgui.get_font_size()+2*imgui.get_style().frame_padding.y    ## height of a standard slider 
        if BUNDLEAPI:
            if imgui.begin_list_box(f"##{label}",ImVec2(wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height))):
                for i,f in enumerate(self._children):
                    if imgui.selectable(f, self._item_current_idx == i)[0]:
                        self._item_current_idx = i
                        self._path=(parent/f).resolve()
                        self._children=None
                imgui.end_list_box()
        else:
            with imgui.begin_list_box("", wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height)) as list_box:
                if list_box.opened:
                    #imgui.listbox_header("",wsize.x-wcursor.x, max((rowcount-1)*height,wsize.y-wcursor.y-3*height))
                    for i,f in enumerate(self._children):
                        if imgui.selectable(f)[1]:
                            self._path=(parent/f).resolve()
                            self._children=None
                    #imgui.listbox_footer()
        imgui.separator()
        imgui.text(str(pathlib.Path(self._path).name))
        if imgui.button("Cancel"):
            imgui.close_current_popup()
            imgui.end_popup()
            return None
        imgui.same_line()
        if imgui.button("Select"):
            imgui.close_current_popup()
            imgui.end_popup()
            return str(self._path)
        imgui.end_popup()
        return None

def pygui_file_open_button(label,path,filterlist=['*']):
    """Displays a button with provided label that popup a file selection dialog when clicked.
    
    Args:
        label: the label of the button.
        path: initial path.
        filterlist: wildcards for file filtering.
    Returns:
        the selected path of None if user cancelled.
    """
    if imgui.button(label):
        imgui.open_popup(label)
    if f:=pygui_popup_file_open_selector(label,path,filterlist):
        return f
    
def pygui_file_save_button(label,path,filterlist=['*']):
    """Displays a button with provided label that popup an editable file selection dialog when clicked.
    
    Args:
        label: the label of the button.
        path: initial path.
        filterlist: wildcards for file filtering.
    Returns:
        the selected path of None if user cancelled.
    """
    if imgui.button(label):
        imgui.open_popup(label)
    if f:=pygui_popup_file_save_selector(label,path,filterlist):
        return f

def pygui_dir_open_button(label,path):
    """Displays a button with provided label that popup a dir selection dialog when clicked
    
    Args:
        label: the label of the button.
        path: initial path
    Returns:
        the selected path of None if user cancelled
    """
    if imgui.button(label):
        imgui.open_popup(label)
    if f:=pygui_popup_dir_open_selector(label,path):
        return f
    
def pygui_image_clickable(texid,ar=1.0,width=None):
    """Displays image with specific aspect ratio and reports mouse clicks.

    Args:
        texid: id of texture
        ar: aspect ratio for image
        center: center the image horizontally (0b01) and/or vertically (0b10)
    Returns:
        tuple (changed, (x,y)) coordinates are relative to width and height (0-1.0 bound)
    """
    width=width if width else pygui_get_content_region_avail()[0]
    pygui_image(texid, width, width*ar, uv0=(0,0),uv1=(1,1))
    lt=imgui.get_item_rect_min()
    rb=imgui.get_item_rect_max()
    xy=imgui.get_mouse_pos()
    if pygui_is_window_focused() and click(0,*lt,*rb):
        return True,pct4(*xy,*lt,*rb)
    return False,(None,None)

def pygui_image_expandable(texid,ar=1.0,center=True):
    """Displays image with specific aspect ratio and optionnaly centered in window.

    Args:
        texid: id of texture
        ar: aspect ratio for image
        center: center the image horizontally (0b01) and/or vertically (0b10)
    Returns:
        None
    """
    width,height=pygui_get_content_region_avail()
    if height/width>ar:
        height=width*ar
    else:
        width=height/ar
    ox,oy=imgui.get_cursor_pos()
    if center & 0b01:
        ox+=(pygui_get_content_region_avail().x-width) * 0.5
    if center &0b10:
        oy+=(pygui_get_content_region_avail().y-height) * 0.5
    imgui.set_cursor_pos((ox,oy))
    pygui_image(texid,width,height,uv0=(0,0),uv1=(1,1))

@static_vars(_x=0,_y=0)
def pygui_image_dragable(texid,ar=1.0,center=True):
    """Displays image and reports the amound of drag when a user drags over the image.

    Args:
        texid: id of texture
        ar: aspect ratio for image
        center: center the image horizontally (0b01) and/or vertically (0b10)
    Returns:
        tuple(changed,(x,y,w)) where w is mouse wheel delta. coordinates are relative to width and height (0-1.0 bound)
    
    notes (1): old implementation uses static var, which may prevent correct operations if the widget is used several times in render loop
    """
    width,height=pygui_get_content_region_avail()
    if height/width>ar:
        height=width*ar
    else:
        width=height/ar
    ox,oy=imgui.get_cursor_pos()
    if center & 0b01:
        ox+=(pygui_get_content_region_avail().x-width) * 0.5
    if center &0b10:
        oy+=(pygui_get_content_region_avail().y-height) * 0.5
    imgui.set_cursor_pos((ox,oy))
    pygui_image(texid,width,height,uv0=(0,0),uv1=(1,1))
    imgui.set_cursor_pos((ox,oy))
    imgui.invisible_button("pygui_image_dragable",*Vec2(width,height))
    lt=imgui.get_item_rect_min()
    rb=imgui.get_item_rect_max()

    ## simple version, but io.mouse_delta is always 0!
    xm,ym=imgui.get_mouse_pos()
    if lt[0]<xm<rb[0] and lt[1]<ym<rb[1]:
        io=imgui.get_io()
        if io.mouse_wheel:
            return (True,(0,0,io.mouse_wheel))
        elif imgui.is_mouse_down(0) and imgui.is_mouse_dragging(0):
            if io.mouse_delta.x!=0 or io.mouse_delta.y!=0:
                return True,(imgui.get_io().mouse_delta.x,imgui.get_io().mouse_delta.y,0)
    return False,(0,0,0)

    xm,ym=imgui.get_mouse_pos()
    if lt[0]<xm<rb[0] and lt[1]<ym<rb[1] and imgui.get_io().mouse_wheel:
        return (True,(0,0,imgui.get_io().mouse_wheel))

    if imgui.is_item_active():
        if imgui.is_item_clicked():
            pygui_image_dragable._x,pygui_image_dragable._y=imgui.get_mouse_pos()
        elif imgui.is_mouse_dragging(0):
            dx,dy=imgui.get_mouse_pos()
            delta=(-dx+pygui_image_dragable._x,
                -dy+pygui_image_dragable._y,
                imgui.get_io().mouse_wheel)
            pygui_image_dragable._x,pygui_image_dragable._y=dx,dy
            return any(delta),delta
    return False,(0,0,0)

@static_vars(_dragging=False)
def pygui_image_roi(texid,roi,ar=1.0,center=True,roi_ar=None,color=[1.0,0.0,0.0,1.0],rounding=0.0, thickness=2.0):
    """Displays image where user can select a rectangular ROI with mouse.

    Args:
        texid: id of texture
        roi: current value of roi (abc.collections with length 4), in % of image width and height
        ar: aspect ratio for image
        center: center the image horizontally (0b01) and/or vertically (0b10)
        roi_ar: forced aspect ratio for roi selection
        color, rounding, thickness: color, corner rounding and line thickness for the selection rect
    Returns:
        tuple(changed,(l,t,r,b))

    notes (1): the roi is always changed whenever mous is pressed but changed is only set when mouse is released
    the correct way to use this is therefore:
        ## in init
        _roi_buffer=(0.0,0.0,0.0,0.0)
        ## in render loop
        imgui.begin_frame()
        changed,_roi_buffer=pygui.image_roi(id, _roi_buffer)
        if changed:
            self.actual_roi=tuple(_roi_buffer)
        imgui.end_frame()

    notes (2): uses static var, which may prevent correct operations if the widget is used several times in render loop
    """
    def pixels4(x,y,l,t,r,b): ## equivalent to pct4
        return([round(l+x*(r-l)),round(t+y*(b-t))])
    
    width,height=pygui_get_content_region_avail()
    if height/width>ar:
        height=width*ar
    else:
        width=height/ar
    ox,oy=imgui.get_cursor_pos()
    if center & 0b01:
        ox+=(pygui_get_content_region_avail().x-width) * 0.5
    if center &0b10:
        oy+=(pygui_get_content_region_avail().y-height) * 0.5
    imgui.set_cursor_pos((ox,oy))
    pygui_image(texid,width,height,uv0=(0,0),uv1=(1,1))
    imgui.set_cursor_pos((ox,oy))
    imgui.invisible_button("pygui_roi_selector",*Vec2(width,height))
    draw_list = imgui.get_window_draw_list()
    l,t,r,b=roi
    lt=imgui.get_item_rect_min()
    rb=imgui.get_item_rect_max()
    xy=imgui.get_mouse_pos()

    if imgui.is_item_active():
        if imgui.is_item_clicked():
            l,t=pct4(*xy,*lt,*rb)
            r,b=l,t
        elif imgui.is_mouse_dragging(0):
            pygui_image_roi._dragging=True
            r,b=pct4(*xy,*lt,*rb)
            if roi_ar:
                b=t+( (r-l)/ar / roi_ar)
    l=clip(l,0.0,1.0)
    t=clip(t,0.0,1.0)
    r=clip(r,0.0,1.0)
    b=clip(b,0.0,1.0)
    if imgui.is_mouse_released(0) and pygui_image_roi._dragging:#and ptinrect(*xy,*lt,*rb):
        ## because pt in rect returns false if mouse is outside the image, we will never reach 1.0 nor 0.0
        ## I prefer using static var to check if we were dragging, to allow selection of full image and avoid bugs when mouse is released outside the image
        pygui_image_roi._dragging=False
        return True, (l,t,r,b)
    l_,t_=pixels4(l,t,lt.x,lt.y,rb.x,rb.y)
    r_,b_=pixels4(r,b,lt.x,lt.y,rb.x,rb.y)

    if BUNDLEAPI:
        _col=imgui.get_color_u32(imgui.ImVec4(*color))
    else:
        _col=imgui.get_color_u32_rgba(*color) ## not tested
    if r_!=l_ and t_!=b_:
        draw_list.add_rect(*Vec2(l_,t_),*Vec2(r_,b_),
                           _col,rounding=rounding,thickness=thickness)
    return False,(l,t,r,b)

def pygui_knob_float(label:str,angle:float,amin:float|None=None,amax:float|None=None)->tuple[bool,float]:
    """Displays a simple knob control that loops over 360°.

    Args:
        label: label of the control. use '##' to provide unique ids.
        angle: the current value of angle (degrees).
        amin, amax:  minimal and maximal values for angle.
    Returns:
        tuple (changed, angle)
    """
    RADIUS=1.3 ## major radius
    radius=0.2 ## minor circle radius
    offset=0.8 ## offset to minor circle center
    thickness=3 ## thickness of outer circle
    
    changed=False
    angle=angle/180*3.14159
    style=imgui.get_style()
    if BUNDLEAPI:
        barcolor=imgui.get_color_u32(imgui.Col_.frame_bg)
        barcolorhovered=imgui.get_color_u32(imgui.Col_.frame_bg_hovered)
        handlecolor=imgui.get_color_u32(imgui.Col_.slider_grab)
        textcolor=imgui.get_color_u32(imgui.Col_.text)
        wori=get_window_pos()
    else:
        barcolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_FRAME_BACKGROUND])
        barcolorhovered=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED])
        handlecolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_SLIDER_GRAB])
        textcolor=imgui.get_color_u32_rgba(*style.colors[imgui.COLOR_TEXT])
        wori=get_window_pos()
    wcursor=imgui.get_cursor_pos()                      ## window coordinates of cursor (top left of next widget,including padding)
    height=imgui.get_font_size()+2*style.frame_padding.y    ## height of a standard slider
    top=wori.y+wcursor.y                                ## top of the bar (screen)
    left=wori.x+wcursor.x                               ## left of bar (screen)
    ## rendering knob and handle
    draw_list = imgui.get_window_draw_list()
    imgui.invisible_button(f"##{label}",*Vec2(height*3,height*3))
    draw_list.add_circle_filled(*Vec2(left+height*1.5, top+height*1.5),
                                    height*1.3,
                                    barcolorhovered if imgui.is_item_hovered() else barcolor,
                                    num_segments=25)
    draw_list.add_circle(*Vec2(left+height*1.5, top+height*1.5),
                                    height*RADIUS,handlecolor,num_segments=25,thickness=thickness)
    l,t,r,b=left,top,left+height*3, top+height*3
    xc,yc=(l+r)//2,(t+b)//2
    xm,ym=imgui.get_mouse_pos()
    if l<xm<r and t<ym<b:
        if imgui.get_io().mouse_wheel:
            inc=3.14159/180 if not imgui.get_io().key_ctrl else 31.4159/180
            angle+=imgui.get_io().mouse_wheel*inc
            changed=True
        if imgui.is_mouse_clicked(0) or imgui.is_mouse_dragging(0):
            adj=xm-xc
            opp=ym-yc
            angle= math.atan2(opp,adj)
            changed=True
    x=xc+(height*offset*math.cos(angle))
    y=yc+(height*offset*math.sin(angle))
    draw_list.add_circle_filled(*Vec2(x,y),radius*height,handlecolor,num_segments=8)
    angle=math.fmod(angle/3.14159*180,360)
    angletext=label+" "+str(int(angle))
    span,h=imgui.calc_text_size(angletext)
    draw_list.add_text(*Vec2(xc-span//2,yc-h//2), textcolor, angletext)
    return changed,angle
