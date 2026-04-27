[2026-04-27]
+ Added `pygui.image_crop` for crop region selection (4 cursor image region selection) 
+ Added `pygui.image_polygon` for n points region selection.
+ Added fillcolor argument to `pygui.image_roi`
+ Rewrote `pygui.range_float2` interaction (still not perfect with classic imgui)
+ Fixed push_id/pop_id issue in test.py for colored range sliders
+ Fixed text input flags for `pygui.file_save_selector`
+ (extra!) Fixed issue in moderngl_window_renderer (render loop updated to imgui>1.86)
+ Probably some other fixes!

[2026-04-25] 
+ Added w_max and h_max parameters to `pygui.image_*` functions to constain the maximum width and height of the image.
+ Set default value of circles (True) for `pygui.time_line` and `pygui.range_float2`.
+ Added bounds parameter to `pygui_pan_and_zoom` to prevent zooming or panning beyond specified limits.
+ Added color option to `pygui.range_float2` and `pygui.time_line` (default is None).
+ Added active option to `pygui.range_float2` to enable early exit (required when multiple controls are stacked close one to each-other).
+ Fixed implementation details in `pygui.image_clickable`.
+ Added Changelog.

[2026-04-24] 
+ Initial release