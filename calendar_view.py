from datetime import date
import calendar

from nicegui import ui



def calendar_view(reservations, change_month_callback, month=None, year=None):

    # Convert reservation dates from strings to dates
    # TODO: discuss with the team if this is changing anywhere else. 
    for r in reservations:
        r['date'] = date.fromisoformat(r['date'])
    
    today = date.today()

    # Default to today 
    year = year or today.year
    month = month or today.month

    # Glad I found this function 
    weeks = calendar.monthcalendar(year, month)


    with ui.column().classes('w-full'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.button(icon='chevron_left', on_click=lambda: change_month_callback(-1)).classes('w-12 h-12')
            ui.label(
                f'{calendar.month_name[month]} {year}'
            ).classes('text-2xl font-bold')
            ui.button(icon='chevron_right', on_click=lambda: change_month_callback(1)).classes('w-12 h-12')

        with ui.grid(columns=7).classes('w-full gap-1'):
            for weekday in [
                'Mon', 'Tue', 'Wed', 'Thu',
                'Fri', 'Sat', 'Sun']:
                ui.label(weekday).classes('font-bold text-center')

            for week in weeks:
                for day in week:
                    if day == 0:
                        ui.card().classes('w-full min-h-36 bg-gray-200')
                        continue

                    current_date = date(year, month, day)

                    with ui.card().classes('w-full min-h-36'):
                        ui.label(str(day)).classes('font-bold')

                        for reservation in reservations:
                            if reservation['date'] == current_date:
                                ui.button(
                                    f"{reservation['slot']} "
                                    f"- {reservation['reserved_by']}",

                                    # TODO: This button should actually open the room details. (Or reservation details if we have that screen)
                                    on_click=lambda: ui.notify("NOT YET IMPLEMENTED: Open room details/reservation details:")
                                )
