import streamlit as st
from streamlit_fullcalendar import fullcalendar

st.title("Streamlit FullCalendar Example")

calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "initialView": "dayGridMonth",
    "events": [
        {
            "title": "MasterCard Event",
            "start": "2024-07-01T08:30:00",
            "end": "2024-07-01T10:30:00"
        }
    ]
}

# Create the calendar component
event = fullcalendar(options=calendar_options)

# Display the clicked event
if event:
    st.write("Event clicked:", event)
