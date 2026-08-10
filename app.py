from datetime import datetime, timedelta
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Train Roster to Google Calendar", page_icon="📅", layout="centered"
)

st.title("📅 Train Crew Roster Converter")
st.write(
    "Convert train crew roster schedules into Google Calendar-ready CSV files instantly."
)

# Sidebar Configuration
st.sidebar.header("Roster Configuration")
start_date = st.sidebar.date_input(
    "Roster Start Date (Sunday)", datetime(2026, 8, 9)
)
user_line = st.sidebar.number_input(
    "Starting Line Number", min_value=1, max_value=100, value=47
)
max_lines = st.sidebar.number_input(
    "Total Lines before looping", min_value=1, max_value=100, value=56
)
total_weeks = st.sidebar.slider(
    "Number of Weeks to Generate", min_value=1, max_value=52, value=52
)

# Text Input for Roster Data
roster_text = st.text_area(
    "Paste Roster Data Here:",
    height=250,
    placeholder="Paste raw text extracted from PDF or spreadsheet (containing lines 1 to 56)...",
)


def parse_roster(text):
    pattern = r'(?:^|\s)((?:(?!RDNA|RD)[A-Z][A-Za-z\-]+\s+)*(?!RDNA|RD)[A-Z][A-Za-z\-]+)\s+(\d{1,2})\s+\d+\s+hrs\s+\d+\s+mins'
    matches = list(re.finditer(pattern, text))
    roster = {}

    for i in range(len(matches)):
        m_curr = matches[i]
        start_pos = m_curr.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        idx = int(m_curr.group(2))
        rest = text[start_pos:end_pos]

        tokens = re.findall(
            r"(RDNA|RD|EX|\d{1,2}:\d{2}\s+\d{1,2}:\d{2}\s+[A-Za-z0-9/]+\s+\d+\.\d{2})",
            rest,
        )

        real_tokens = []
        j = 0
        while j < len(tokens):
            if tokens[j] == "EX":
                j += 1
                continue
            val = tokens[j]
            if j + 1 < len(tokens) and tokens[j + 1] == "EX":
                val += " [EX]"
            real_tokens.append(val)
            j += 1

        roster[idx] = real_tokens[:7]
    return roster


if st.button("Generate Calendar File", type="primary"):
    if not roster_text.strip():
        st.error("Please paste roster text before generating.")
    else:
        try:
            roster = parse_roster(roster_text)
            if len(roster) == 0:
                st.warning(
                    "No valid roster lines found. Check text formatting."
                )
            else:
                events = []
                current_line = int(user_line)

                for week in range(total_weeks):
                    if current_line not in roster:
                        current_line = 1  # Fallback reset if missing line

                    shifts = roster[current_line]
                    for day_idx in range(min(7, len(shifts))):
                        current_date = start_date + timedelta(
                            days=week * 7 + day_idx
                        )
                        shift = shifts[day_idx]

                        if shift not in ["RD", "RDNA"]:
                            parts = shift.replace(" [EX]", "").split()
                            if len(parts) >= 4:
                                on_time, off_time, turn, hours = (
                                    parts[0],
                                    parts[1],
                                    parts[2],
                                    parts[3],
                                )

                                on_dt = datetime.strptime(on_time, "%H:%M")
                                off_dt = datetime.strptime(off_time, "%H:%M")

                                on_str = on_dt.strftime("%I:%M %p")
                                off_str = off_dt.strftime("%I:%M %p")

                                end_date = current_date
                                if off_dt < on_dt:
                                    end_date += timedelta(days=1)

                                events.append({
                                    "Subject": f"{turn} ({hours})",
                                    "Start Date": current_date.strftime(
                                        "%m/%d/%Y"
                                    ),
                                    "Start Time": on_str,
                                    "End Date": end_date.strftime("%m/%d/%Y"),
                                    "End Time": off_str,
                                    "All Day Event": "False",
                                    "Description": f"{turn} ({hours}) hrs",
                                })

                    current_line += 1
                    if current_line > max_lines:
                        current_line = 1

                df = pd.DataFrame(events)

                st.success(
                    f"Successfully generated {len(df)} shifts across {total_weeks} weeks!"
                )
                st.dataframe(df.head(10))

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Google Calendar CSV",
                    data=csv,
                    file_name="roster_calendar_import.csv",
                    mime="text/csv",
                )
        except Exception as e:
            st.error(f"Error processing roster: {e}")
