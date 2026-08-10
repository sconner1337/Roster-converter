from datetime import datetime, timedelta
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Train Roster to Google Calendar", page_icon="📅", layout="centered"
)

# Hardcoded Roster Data
ROSTER_TEXT = """
V BONIFACE 1 17 hrs 25 mins RDNA RDNA RDNA RDNA RDNA 5:05 14:23 A/R 9.18 EX 4:15 12:22 103 8.07 RDNA N HEALY 2 25 hrs 35 mins 3:50 11:50 251 8.00 3:50 12:07 51 8.17 5:05 14:23 A/R 9.18 RDNA RDNA RDNA RDNA V AMLA 3 52 hrs 11 mins 12:52 20:38 211 7.46 13:00 22:18 A/R 9.18 13:00 22:18 A/R 9.18 14:22 22:37 12 8.15 14:45 0:03 A/R 9.18 16:07 0:23 15 8.16 RD C HARRISON 4 34 hrs 07 mins RDNA RDNA RDNA 3:50 12:15 1 8.25 3:50 12:07 51 8.17 4:00 12:07 2 8.07 5:05 14:23 A/R 9.18 Z KARHANI 5 26 hrs 19 mins 4:40 12:23 203 7.43 EX 5:05 14:23 A/R 9.18 EX RDNA RDNA RD EX RD EX 14:37 23:55 A/R 9.18 14:55 0:12 A/R 9.17 16:07 0:23 15 8.16 13:37 21:52 11 8.15 12:22 20:52 10 8.30 SA REHMAN 6 37 hrs 15 mins 14:23 23:37 212 9.14 14:22 23:40 A/R 9.18 15:30 0:55 14 9.25 15:15 0:33 A/R 9.18 RDNA RDNA RDNA A HENNING 7 43 hrs 57 mins RDNA RDNA 3:50 12:15 1 8.25 4:11 12:22 3 8.11 6:37 15:55 A/R 9.18 5:23 14:08 5 8.45 5:15 14:33 A/R 9.18 K SNODDEN 8 27 hrs 54 mins RDNA RDNA RDNA RDNA 14:37 0:02 13 9.25 14:22 23:40 A/R 9.18 14:22 23:33 112 9.11 J HORSWELL 9 28 hrs 01 mins 14:40 23:58 A/R 9.18 14:37 0:02 13 9.25 14:38 23:56 A/R 9.18 RDNA RDNA RDNA RDNA TS GREENWAY 10 50 hrs 46 mins 5:45 15:03 A/R 9.18 EX 5:23 14:08 5 8.45 EX 4:11 12:22 3 8.11 EX 4:23 12:37 4 8.14 EX 4:00 12:07 2 8.07 EX 4:11 12:22 3 8.11 EX RDNA 15:00 0:18 A/R 9.18 16:22 1:14 16 8.52 16:07 0:23 15 8.16 17:07 1:00 17 7.53 15:10 0:28 A/R 9.18 17:00 1:00 54 8.00 T GODINHO 11 35 hrs 21 mins RDNA RDNA RDNA 15:10 0:28 A/R 9.18 16:22 1:14 16 8.52 17:07 1:00 17 7.53 15:00 0:18 A/R 9.18 ND LE-GRANGE 12 27 hrs 25 mins 15:23 1:00 213 9.37 15:10 0:28 A/R 9.18 RDNA RDNA RDNA RDNA 6:37 15:07 152 8.30 DP GODDEN 13 45 hrs 08 mins 7:15 16:33 A/R 9.18 7:23 15:37 7 8.14 7:37 16:55 A/R 9.18 7:30 16:30 704 9.00 7:37 16:55 A/R 9.18 RDNA RD A HEWITT 14 45 hrs 05 mins RDNA RDNA 14:20 23:38 A/R 9.18 13:37 22:37 53 9.00 13:37 22:37 53 9.00 15:10 0:28 A/R 9.18 16:37 1:06 115 8.29 S JOHAL 15 17 hrs 15 mins RDNA RDNA RDNA RDNA RDNA 7:52 16:52 8 9.00 6:37 14:52 106 8.15 A BAILEY 16 27 hrs 18 mins 5:50 15:08 A/R 9.18 7:30 16:30 701 9.00 7:52 16:52 8 9.00 RDNA RDNA RDNA RDNA S BENNETT 17 51 hrs 37 mins 15:00 0:18 A/R 9.18 EX 16:22 1:14 16 8.52 EX 16:07 0:23 15 8.16 EX 17:07 1:00 17 7.53 EX 15:10 0:28 A/R 9.18 EX 17:00 1:00 54 8.00 EX RDNA 5:45 15:03 A/R 9.18 5:23 14:08 5 8.45 4:11 12:22 3 8.11 4:23 12:37 4 8.14 4:00 12:07 2 8.07 4:11 12:22 3 8.11 Vacancy 18 34 hrs 33 mins RD RD RD 5:10 14:28 A/R 9.18 6:20 15:19 6 8.59 4:23 12:37 4 8.14 3:50 11:52 151 8.02 Vacancy 19 24 hrs 18 mins 3:50 10:39 201 6.49 4:11 12:22 3 8.11 RD RD RD RD 14:55 0:13 A/R 9.18 3:50 10:39 A/R 6.49 4:11 12:22 A/R 8.11 Vacancy 20 33 hrs 07 mins 16:53 0:49 216 7.56 17:07 1:00 17 7.53 15:15 0:33 A/R 9.18 17:00 1:00 54 8.00 RD RD RD N LOTA 21 44 hrs 04 mins RDNA RDNA 7:30 16:30 703 9.00 7:37 16:55 A/R 9.18 7:23 15:37 52 8.14 7:23 15:37 52 8.14 7:00 16:18 A/R 9.18 G HUGENTOBLER-AYRES 22 28 hrs 01 mins RD RD EX RD RD 14:22 23:40 A/R 9.18 14:37 0:02 13 9.25 14:50 0:08 A/R 9.18 12:22 20:52 10 8.30 S ARINZE 23 25 hrs 48 mins 15:52 0:07 215 8.15 EX 14:45 0:03 A/R 9.18 14:22 22:37 12 8.15 RD RD RD RD RDNA C DOBREA 24 53 hrs 21 mins 6:10 15:28 A/R 9.18 6:20 15:19 6 8.59 EX 5:15 14:33 A/R 9.18 7:23 15:37 52 8.14 7:23 15:37 7 8.14 7:38 16:56 A/R 9.18 RDNA RDNA N RAI 25 36 hrs 42 mins RDNA RDNA RDNA 14:37 0:02 13 9.25 14:20 23:38 A/R 9.18 13:37 22:37 53 9.00 12:38 21:37 111 8.59 V CHHABRA 26 26 hrs 51 mins 14:41 23:59 A/R 9.18 14:22 22:37 12 8.15 RDNA RDNA RD EX RDNA 7:30 16:48 A/R 9.18 3:50 12:15 1 8.25 MA ALI 27 42 hrs 17 mins 6:53 15:08 252 8.15 EX 7:37 16:55 A/R 9.18 EX 7:23 15:37 52 8.14 EX 7:52 16:52 8 9.00 EX 10:00 17:30 9 7.30 EX RDNA RDNA 12:00 20:16 209 8.16 14:25 23:43 A/R 9.18 13:37 22:37 53 9.00 14:15 23:33 A/R 9.18 RDNA A DUCZEK 28 44 hrs 46 mins RDNA RD EX 13:37 21:52 11 8.15 12:22 20:52 10 8.30 13:00 22:18 A/R 9.18 14:20 23:38 A/R 9.18 15:52 1:17 113 9.25 6:20 15:19 6 8.59 S FURLONG 29 17 hrs 36 mins RDNA RDNA RDNA RDNA RDNA 5:15 14:33 A/R 9.18 4:55 13:13 105 8.18 N HANSEN 30 25 hrs 01 mins 4:05 11:23 202 7.18 EX 3:50 12:15 1 8.25 EX 6:37 15:55 A/R 9.18 EX RD RD RD RD 14:20 23:37 A/R 9.17 13:37 21:52 11 8.15 15:10 0:27 A/R 9.17 B SHAH 31 51 hrs 37 mins 12:52 20:52 253 8.00 14:20 23:38 A/R 9.18 16:22 1:14 16 8.52 16:07 0:23 15 8.16 17:07 1:00 17 7.53 15:07 0:25 A/R 9.18 RD EX 14:55 0:12 A/R 9.17 O FITZGERALD 32 33 hrs 39 mins RDNA RDNA RDNA 5:23 14:08 5 8.45 5:15 14:33 A/R 9.18 6:20 15:19 6 8.59 4:00 10:37 102 6.37 N DIVINYECZ 33 27 hrs 02 mins 6:05 15:23 A/R 9.18 7:23 15:37 52 8.14 RDNA RDNA RDNA RDNA 13:00 22:30 109 9.30 F KERECUK 34 35 hrs 52 mins 12:00 20:16 209 8.16 EX 14:25 23:43 A/R 9.18 EX 13:37 22:37 53 9.00 EX 14:15 23:33 A/R 9.18 EX RD EX RDNA RDNA 6:53 15:08 252 8.15 7:37 16:55 A/R 9.18 7:23 15:37 52 8.14 7:52 16:52 8 9.00 10:00 17:30 9 7.30 I MCLAGAN 35 43 hrs 17 mins RDNA RDNA 7:23 15:37 7 8.14 7:38 16:56 A/R 9.18 7:52 16:52 8 9.00 10:00 17:30 9 7.30 8:37 17:52 108 9.15 E MORRIS 36 26 hrs 43 mins RDNA RDNA RDNA RDNA 14:22 22:37 12 8.15 14:30 23:48 A/R 9.18 16:07 1:17 114 9.10 G SIDHU 37 26 hrs 33 mins 15:22 0:37 214 9.15 15:15 0:33 A/R 9.18 17:00 1:00 54 8.00 RDNA RDNA RDNA RDNA C COWELL 38 50 hrs 30 mins 8:38 17:54 208 9.16 7:52 16:52 8 9.00 10:00 17:30 9 7.30 10:00 17:30 9 7.30 7:30 16:30 702 9.00 7:23 15:37 7 8.14 RD EX 16:52 0:48 116 7.56 G BHULLAR 39 35 hrs 03 mins RD EX RDNA RDNA 14:22 23:40 A/R 9.18 13:37 21:52 11 8.15 EX 12:22 20:52 10 8.30 EX 12:37 21:37 110 9.00 15:52 0:07 215 8.15 RDNA RDNA Z RABBANI 40 26 hrs 50 mins 13:50 23:08 A/R 9.18 15:30 0:55 14 9.25 RDNA RDNA RDNA RD EX 3:45 11:52 101 8.07 6:40 15:10 A/R 8.30 M POONIA 41 42 hrs 38 mins 4:40 13:30 204 8.50 4:00 12:07 2 8.07 3:50 12:07 51 8.17 4:00 12:07 2 8.07 5:05 14:22 A/R 9.17 RDNA RDNA M HINGSTON 42 44 hrs 44 mins RDNA RDNA 12:22 20:52 10 8.30 13:00 22:17 A/R 9.17 15:30 0:55 14 9.25 14:22 22:37 12 8.15 13:50 23:07 A/R 9.17 DD OBILLO 43 17 hrs 04 mins RD RD RDNA RDNA RDNA 3:50 12:15 1 8.25 4:33 13:12 104 8.39 D GILPIN 44 24 hrs 53 mins 5:10 13:35 205 8.25 4:23 12:37 4 8.14 4:23 12:37 4 8.14 RD EX RD EX RDNA RD EX 3:50 12:07 51 8.17 6:40 15:10 A/R 8.30 5:20 14:37 A/R 9.17 A SALAMON 45 53 hrs 25 mins 12:40 21:39 210 8.59 EX 13:37 22:37 53 9.00 EX 14:22 23:39 A/R 9.17 EX 16:22 1:14 16 8.52 EX 17:00 1:00 54 8.00 EX 15:15 0:32 A/R 9.17 EX RDNA 6:40 15:50 A/R 9.10 6:40 15:10 A/R 8.30 6:40 15:10 A/R 8.30 6:40 15:10 A/R 8.30 RDNA RDNA Vacancy 46 34 hrs 43 mins RD RD RD 6:20 15:19 6 8.59 4:11 12:22 3 8.11 7:37 16:55 A/R 9.18 6:52 15:07 107 8.15 M MIELNICZUK 47 26 hrs 04 mins 8:00 17:17 A/R 9.17 10:00 17:30 9 7.30 RDNA RDNA RDNA RDNA 13:52 23:09 A/R 9.17 E ODIAKA 48 33 hrs 10 mins 16:37 0:37 254 8.00 17:00 1:00 54 8.00 17:07 1:00 17 7.53 15:07 0:24 A/R 9.17 RD RD RD A MAHMOOD 49 42 hrs 23 mins RDNA RDNA 4:00 12:07 2 8.07 3:50 12:07 51 8.17 EX 3:50 12:15 1 8.25 EX 3:50 12:07 51 8.17 5:20 14:37 A/R 9.17 EX RDNA RDNA RDNA N GIBBONS 50 24 hrs 52 mins RDNA RDNA RDNA RDNA 12:22 20:52 10 8.30 13:37 21:52 11 8.15 14:00 22:07 153 8.07 K UNDERHILL 51 26 hrs 49 mins 14:20 23:37 A/R 9.17 EX 13:37 21:52 11 8.15 EX 15:10 0:27 A/R 9.17 EX RDNA RDNA RDNA RDNA 4:05 11:23 202 7.18 3:50 12:15 1 8.25 6:37 15:55 A/R 9.18 K THANKI 52 53 hrs 05 mins 7:08 15:09 207 8.01 5:15 14:32 A/R 9.17 6:20 15:19 6 8.59 5:05 14:22 A/R 9.17 4:23 12:37 4 8.14 5:55 15:12 A/R 9.17 RDNA V PANTELEJEV 53 34 hrs 53 mins RDNA RDNA RDNA 13:37 21:52 11 8.15 15:15 0:32 A/R 9.17 15:30 0:55 14 9.25 16:52 0:48 116 7.56 EX RDNA L SMITH 54 26 hrs 50 mins 14:55 0:12 A/R 9.17 EX 16:07 0:23 15 8.16 EX RDNA RDNA RDNA RDNA 5:10 14:27 A/R 9.17 4:40 12:23 203 7.43 5:05 14:23 A/R 9.18 Vacancy 55 43 hrs 01 mins 6:53 14:53 206 8.00 5:57 15:14 A/R 9.17 5:23 14:08 5 8.45 7:23 15:37 7 8.14 5:23 14:08 5 8.45 RD RD A KUMAR 56 45 hrs 16 mins RDNA RDNA 14:30 23:47 711 9.17 15:30 0:55 14 9.25 15:07 0:24 A/R 9.17 16:22 1:14 16 8.52 16:52 1:17 154 8.25
"""

@st.cache_data
def load_roster_data():
    """Parses the hardcoded roster text and maps names to their line number and shifts."""
    pattern = r'(?:^|\s)((?:(?!RDNA|RD)[A-Z][A-Za-z\-]+\s+)*(?!RDNA|RD)[A-Z][A-Za-z\-]+)\s+(\d{1,2})\s+\d+\s+hrs\s+\d+\s+mins'
    matches = list(re.finditer(pattern, ROSTER_TEXT))
    
    roster = {}
    name_to_line = {}
    
    for i in range(len(matches)):
        m_curr = matches[i]
        start_pos = m_curr.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(ROSTER_TEXT)
        
        raw_name = m_curr.group(1).strip()
        idx = int(m_curr.group(2))
        rest = ROSTER_TEXT[start_pos:end_pos]
        
        # Handle duplicate "Vacancy" names so they show up uniquely in the dropdown
        display_name = f"{raw_name} (Line {idx})" if "Vacancy" in raw_name else raw_name
        name_to_line[display_name] = idx
        
        # Extract the shift logic, including EX overrides
        tokens = re.findall(r"(RDNA|RD|EX|\d{1,2}:\d{2}\s+\d{1,2}:\d{2}\s+[A-Za-z0-9/]+\s+\d+\.\d{2})", rest)
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
        
    return roster, name_to_line

# Load Data
roster, name_to_line = load_roster_data()

st.title("📅 Train Crew Calendar Generator")
st.write("Select your name to instantly generate your personalized 52-week Google Calendar file.")

# Simple Dropdown for Users
selected_name = st.selectbox("Select your name from the roster:", options=sorted(name_to_line.keys()))
start_date = st.date_input("Roster Start Date (Sunday)", datetime(2026, 8, 9))

if st.button("Generate My Calendar", type="primary"):
    try:
        events = []
        user_line = name_to_line[selected_name]
        current_line = user_line
        max_lines = 56
        total_weeks = 52

        for week in range(total_weeks):
            if current_line not in roster:
                current_line = 1  # Fallback

            shifts = roster[current_line]
            for day_idx in range(min(7, len(shifts))):
                current_date = start_date + timedelta(days=week * 7 + day_idx)
                shift = shifts[day_idx]

                if shift not in ["RD", "RDNA"]:
                    parts = shift.replace(" [EX]", "").split()
                    if len(parts) >= 4:
                        on_time, off_time, turn, hours = parts[0], parts[1], parts[2], parts[3]

                        on_dt = datetime.strptime(on_time, "%H:%M")
                        off_dt = datetime.strptime(off_time, "%H:%M")

                        on_str = on_dt.strftime("%I:%M %p")
                        off_str = off_dt.strftime("%I:%M %p")

                        end_date = current_date
                        if off_dt < on_dt:
                            end_date += timedelta(days=1)

                        events.append({
                            "Subject": f"{turn} ({hours})",
                            "Start Date": current_date.strftime("%m/%d/%Y"),
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

        st.success(f"Success! Generated {len(df)} shifts across {total_weeks} weeks for {selected_name}.")
        st.dataframe(df.head(10))

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Google Calendar CSV",
            data=csv,
            file_name=f"{selected_name.replace(' ', '_')}_calendar.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Error processing roster: {e}")
