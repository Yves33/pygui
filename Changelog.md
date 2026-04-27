[2026-04-26]
Fixed push_id/pop_id issue in test for colored range sliders
Fixed text input flages for file_save_selector
(extra!) Fixed issue in moderngl_window_renderer (render loop updated to imgui>1.86)
range_float2 interactions rewrite (cleaner, no static vars)

[2026-04-25] 
Added w_max and h_max parameters to image_* functions to constain the maximum size of the image.
Set default value of circles (True) for pygui.time_line and pygui.range_float2.
Added bounds parameter to pygui_pan_and_zoom to prevent zooming or panning beyond specified limits.
Added color option to pygui.range_float2 and pygui.time_line (default is None).
Added active option to pygui.range_float2 to enable early exit (required when multiple controls are stacked close one to each-other)
Fixed implementation details in image_clickable.
Added Changelog.

[2026-04-24] 
Initial release