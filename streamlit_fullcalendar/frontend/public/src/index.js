import { withStreamlitConnection } from "streamlit-component-lib";
import { Calendar } from "@fullcalendar/core";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";

const app = document.getElementById("app");

function FullCalendarComponent(events, options) {
    const calendar = new Calendar(app, {
        plugins: [dayGridPlugin, interactionPlugin],
        events: events,
        ...options,
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            Streamlit.setComponentValue({
                title: info.event.title,
                start: info.event.start,
                end: info.event.end,
            });
        }
    });
    calendar.render();
}

export function render(events, options) {
    FullCalendarComponent(events, options);
}

withStreamlitConnection(render);
