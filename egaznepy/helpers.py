def jupyter_use_whole_width_fix():
    from IPython.display import HTML, display

    display(HTML("<style>.container { width:100% !important; }</style>"))
