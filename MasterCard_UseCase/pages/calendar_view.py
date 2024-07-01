import streamlit as st
from streamlit_calendar import calendar

st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
st.sidebar.divider()
st.sidebar.page_link("app.py", label="**Accueil**", icon="🏠")
st.sidebar.page_link("pages/results_recon.py", label="**:alarm_clock: Historique**")
st.sidebar.page_link("pages/MasterCard_UI.py", label="**🔀 MasterCard Network Reconciliaiton Option**")
st.sidebar.page_link("pages/calendar_view.py", label="**📆 Vue Agenda**")
calendar_options = {
    "editable": "true",
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth"
    },
    "slotMinTime": "08:00:00",
    "slotMaxTime": "19:00:00",
    "initialView": "dayGridMonth",
    "contentHeight": 1000,
    "aspectRatio": 1.35

}
calendar_events = [
    {
        "allDay": True,
        "title": "MasterCard",
        "start": "2024-07-01T08:30:00",
        "end": "2024-07-01T10:30:00",
        "backgroundColor": "#ff5f00",
        "borderColor": "#f79e1b"
    },
    {
        "allDay": True,
        "title": "Visa",
        "start": "2024-07-01T08:30:00",
        "end": "2024-07-01T10:30:00",
        "backgroundColor": "#1A1F71",
        "borderColor": "#F7B600"
    },
    {
        "allDay": True,
        "title": "Amex",
        "start": "2024-07-01T08:30:00",
        "end": "2024-07-01T10:30:00",
        "backgroundColor": "016FD0",
        "borderColor": "#FFFFF"
    },
    {
        "allDay": True,
        "title": "Amex",
        "start": "2024-07-03T08:30:00",
        "end": "2024-07-03T10:30:00",
        "backgroundColor": "016FD0",
        "borderColor": "#FFFFF"
    },
    {
        "allDay": True,
        "title": "MasterCard",
        "start": "2024-07-04T08:30:00",
        "end": "2024-07-04T10:30:00",
        "backgroundColor": "#ff5f00",
        "borderColor": "#f79e1b"
    },
    {
        "allDay": True,
        "title": "Amex",
        "start": "2024-07-05T08:30:00",
        "end": "2024-07-05T10:30:00",
        "backgroundColor": "016FD0",
        "borderColor": "#FFFFF"
    },
    {
        "allDay": True,
        "title": "Visa",
        "start": "2024-07-08T08:30:00",
        "end": "2024-07-08T10:30:00",
        "backgroundColor": "#1A1F71",
        "borderColor": "#F7B600"
    },
    {
        "allDay": True,
        "title": "Visa",
        "start": "2024-07-07T08:30:00",
        "end": "2024-07-07T10:30:00",
        "backgroundColor": "#1A1F71",
        "borderColor": "#F7B600"
    },
    {
        "allDay": True,
        "title": "Visa",
        "start": "2024-07-03T08:30:00",
        "end": "2024-07-03T10:30:00",
        "backgroundColor": "#1A1F71",
        "borderColor": "#F7B600"
    },
    {
        "allDay": True,
        "title": "MasterCard",
        "start": "2024-07-07T08:30:00",
        "end": "2024-07-07T10:30:00",
        "backgroundColor": "#ff5f00",
        "borderColor": "#f79e1b"
    },
    {
        "allDay": True,
        "title": "China Union Pay",
        "start": "2024-07-04T08:30:00",
        "end": "2024-07-04T10:30:00",
        "backgroundColor": "#e22029",
        "borderColor": "#045065"
    },
]
custom_css = """
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""

calendar = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
# st.write(calendar)
