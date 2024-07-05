import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "fullcalendar",
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
)

def fullcalendar(events, options):
    component_value = _component_func(events=events, options=options)
    return component_value
