
# ------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- SETUP --------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
import time as tm
from datetime import time, date


st.set_page_config(page_title="Horse Racing DB", layout="wide")
st.title("🐎 Horse Racing Database") 

st.markdown("""
<style>
/* Clean page background */
.stApp {
  background-color: #FFFFFF !important;
  color: #665326 !important;
}

/* Gradient buttons (English Red → Medium Vermilion) */
.stButton > button {
  background: linear-gradient(135deg, #AE3B4C, #D9693F) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 0.55em 1.1em !important;
  font-weight: 600 !important;
  transition: transform .15s ease, filter .15s ease;
}

.stButton > button:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
  background-color: #F8F6F3 !important;
  color: #665326 !important;
}

.dataframe, .stMarkdown {
  color: #665326 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- DB CONNECTION ----------
# Building the connection
ENGINE = create_engine(
    "mysql+pymysql://root:meme2004@localhost:3306/horse_racing_db",
    pool_pre_ping=True, # checks connections before using them.
    future=True         # makes SQLAlchemy use its modern syntax and behavior (future-proof).
)

# This is the “query” function — it runs a SQL SELECT statement and returns the results as a pandas DataFrame.
def q(sql, params=None) -> pd.DataFrame:
    with ENGINE.begin() as cx:
        rows = cx.execute(text(sql), params or {}).mappings().all()
    return pd.DataFrame(rows)

# This one is for “execute” — used for any command that changes data: INSERT, UPDATE, DELETE, ALTER TABLE, etc.
def x(sql, params=None):
    with ENGINE.begin() as cx:
        return cx.execute(text(sql), params or {})

# ---------- Reload data from db.sql ----------
def run_sql_script(script_path="db.sql"):
    sql_text = Path(script_path).read_text(encoding="utf-8")

    # remove single-line comments
    lines = []
    for ln in sql_text.splitlines():
        s = ln.strip()
        if s.startswith("--") or s.startswith("#"):
            continue
        lines.append(ln)
    sql_text = "\n".join(lines)

    # very simple split by semicolon
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]

    with ENGINE.begin() as cx:
        cx.exec_driver_sql("SET FOREIGN_KEY_CHECKS=0;")
        for stmt in statements:
            cx.exec_driver_sql(stmt)
        cx.exec_driver_sql("SET FOREIGN_KEY_CHECKS=1;")


# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Role switch (Sidebar) ------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------

if "role" not in st.session_state:
    st.session_state.role = "Default"   # Default until selected
if "view" not in st.session_state:
    st.session_state.view = "home"

with st.sidebar:
    st.markdown("### 🎭 Choose a role")
    role_options = ["Select role", "Guest", "Admin"]
    selected_role = st.selectbox(
        "Select your role",
        role_options,
        index=role_options.index(
            st.session_state.role if st.session_state.role in role_options else "Select role"
        ),
        key="role_select",
        label_visibility="collapsed",
    )

# Handle selection
if selected_role != st.session_state.role:
    st.session_state.role = selected_role
    st.session_state.view = "home"
    st.rerun()

# Stop if no role selected
if st.session_state.role == "Select role" or st.session_state.role == "Default":
    st.warning("👋 Please choose a role to continue.")
    st.stop()
# ------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------- NAV / ROUTER -----------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------

PAGES = {
    "🏁 Add Race + Results": "add_race",
    "🧹 Delete Owner (+ related)": "delete_owner",
    "↔️ Move Horse Between Stables": "move_horse",
    "✅ Approve Trainer": "approve_trainer",
}

# init selected view
if "view" not in st.session_state:
    st.session_state.view = "home"

def go(view: str):
    st.session_state.view = view
    st.rerun()

def admin_home():
    st.caption("Choose an admin function")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🏁 Add a new race with its results")
        if st.button("Add Race", use_container_width=True):
            go("add_race")

        st.markdown("### ↔️ Move a horse to another stable")
        if st.button("Move Horse", use_container_width=True):
            go("move_horse")

    with c2:
        st.markdown("### 🧹 Delete an owner and related info")
        if st.button("Delete Owner", use_container_width=True):
            go("delete_owner")

        st.markdown("### ✅ Approve a new trainer to join a stable")
        if st.button("Approve Trainer", use_container_width=True):
            go("approve_trainer")

    st.divider()
    with st.expander("Reset sample data (reload from db.sql)"):
        if st.button("Reload data from db.sql"):
            try:
                run_sql_script("db.sql")
                st.success("Sample data reloaded from db.sql.")
            except Exception as e:
                st.error(f"Reload failed: {e}")

def guest_home():
    st.caption("Choose a guest function")
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("### 👤 Horses owned by last name")
        if st.button("Horses by Owner", use_container_width=True):
            go("g_owners_horses")

        st.markdown("### 🏆 Trainers who trained winners")
        if st.button("Trainer Winners", use_container_width=True):
            go("g_trainer_winners")  

    with g2:
        st.markdown("### 💰 Trainer winnings (total prize)")
        if st.button("Trainer Winnings", use_container_width=True):
            go("g_trainer_winnings")

        st.markdown("### 🏟️ Track stats (races & participants)")
        if st.button("Track Stats", use_container_width=True):
            go("g_track_stats")


def backbar(home_view: str):
    """back-to-home button."""
    if st.button("← Home", key=f"back_{home_view}"):
        go(home_view)     
        st.stop()         # prevent the rest of the page from rendering

# ------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- ADMIN --------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------ Feature (1): Adding a new race with the results of the race -----------------------------------
# ---------- helpers ----------
# Helper(1): Automatically generate a new race ID like race37 or race101 based on the highest existing race ID in the database.
def next_race_id() -> str:
    """Generate raceNN based on current max"""
    df = q("SELECT MAX(CAST(SUBSTRING(raceId,5) AS UNSIGNED)) AS n "
           "FROM Race WHERE raceId LIKE 'race%'")
    n = int(df.iloc[0]["n"] or 0) + 1
    return f"race{n}"

# Helper(2): Race Exisitance Check
def race_exists(race_id: str) -> bool:
    """Checks if a race already exists in DB"""
    df = q("SELECT 1 FROM Race WHERE raceId=:rid LIMIT 1", {"rid": race_id})
    return not df.empty

# ---------- UI: Add Race + Results ----------
def render_add_race():
    st.markdown("#### 🏁 Add a new race and its results")
    if st.button("← Home"):
        go("home")

    RESULT_OPTIONS = ["first", "second", "third", "fourth", "last", "no show"] # As found in the appendix 

    st.subheader("Add a new race and its results")

    # fetch dropdown data
    tracks = q("SELECT trackName FROM Track ORDER BY trackName")
    horses = q("SELECT horseId, horseName FROM Horse ORDER BY horseName")

    # A quick validation: ensuring that the form only appears if the database has data.
    if tracks.empty or horses.empty:
        st.warning("You need tracks and horses in the database before adding a race.")
        st.stop()

    # Form Fields 
    st.caption("Race ID will be assigned automatically on create.")
    race_name = st.text_input("Race name")
    track_label = st.selectbox("Track", tracks["trackName"].tolist())
    race_date = st.date_input("Race date", value=date.today())
    race_time = st.time_input("Race time", value=time(7, 0))

    # choose participating horses
    labels = horses.apply(lambda r: f"{r['horseName']} (#{r['horseId']})", axis=1).tolist()
    chosen_labels = st.multiselect("Participating horses (top item will be winner if you choose so)",
                                  labels, max_selections=len(labels))

    # per-horse results & prize
    entries = []
    if chosen_labels:
        st.markdown("**Set result and prize for each horse**")
        for lbl in chosen_labels:
            hid = lbl.split("#")[-1][:-1]
            cname = lbl.split(" (#")[0]
            c1, c2 = st.columns([2,1])
            with c1:
                res = st.selectbox(f"Result for {cname}", RESULT_OPTIONS, key=f"res_{hid}")
            with c2:
                prize = st.number_input(f"Prize for {cname}", min_value=0.0, step=100.0, key=f"pr_{hid}")
            entries.append((hid, res, prize))

    # ---------- VALIDATION ----------
    def validate() -> list[str]:
        errors = []
        if not track_label:
            errors.append("Track is required.")
        if not chosen_labels:
            errors.append("Select at least one horse.")
        seen = set()
        for hid, res, prize in entries:
            if hid in seen:
                errors.append("Duplicate horse selected.")
                break
            seen.add(hid)
            if res not in RESULT_OPTIONS:
                errors.append(f"Invalid result for horse {hid}.")
            if prize is None or prize < 0:
                errors.append(f"Prize must be ≥ 0 for horse {hid}.")
        return errors
    # ---------- SUBMIT ----------
    if st.button("Create race with results", type="primary"):
        errs = validate()
        if errs:
            for e in errs:
                st.error(e)
        else:
            try:
                # generate a unique race id right before inserting
                rid = next_race_id()

                with ENGINE.begin() as cx:
                    # insert race into Race table
                    cx.execute(text("""
                        INSERT INTO Race (raceId, raceName, trackName, raceDate, raceTime)
                        VALUES (:id, :nm, :trk, :dt, :tm)
                    """), {"id": rid, "nm": race_name or None, "trk": track_label,
                          "dt": race_date, "tm": race_time})

                    # insert results into Results table
                    for hid, res, prize in entries:
                        cx.execute(text("""
                            INSERT INTO RaceResults (raceId, horseId, results, prize)
                            VALUES (:rid, :hid, :res, :pr)
                        """), {"rid": rid, "hid": hid, "res": res, "pr": prize})

                st.success(f"Race **{rid}** created with {len(entries)} result(s).")

                # UI Repoerter: Confirms that all RaceResults were added successfully
                preview = q("""
                    SELECT rr.raceId, rr.horseId, h.horseName, rr.results, rr.prize
                    FROM RaceResults rr
                    JOIN Horse h ON h.horseId = rr.horseId
                    WHERE rr.raceId = :rid
                    ORDER BY rr.prize DESC
                """, {"rid": rid})
                st.dataframe(preview, use_container_width=True)

            except Exception as e:
                st.error(f"Failed to create race: {e}")

# ---------------------------------------- Feature (2):  Delete an owner and all related info ----------------------------------------
def ensure_db_programs():
    """Create old_info table, the AFTER DELETE trigger, and the stored procedure
    if they don't already exist. Runs safely every time the app starts."""
    with ENGINE.begin() as cx:

        
# ---------- Archive table ----------
        # 0) Ensure the archive table exists (for the trigger)
        cx.execute(text("""
            CREATE TABLE IF NOT EXISTS old_info (
              horseId      VARCHAR(15) NOT NULL,
              horseName    VARCHAR(15) NOT NULL,
              age          INT,
              gender       CHAR(1),
              registration INT NOT NULL,
              stableId     VARCHAR(30) NOT NULL,
              deleted_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

# ---------- trigger ----------
        # 1) Trigger: copy deleted horses into old_info
        trig_exists = cx.execute(text("""
            SELECT COUNT(*) FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA = DATABASE()
              AND TRIGGER_NAME   = 'trg_horse_to_oldinfo'
        """)).scalar()

        if not trig_exists:
            # DROP for idempotency then CREATE
            cx.execute(text("DROP TRIGGER IF EXISTS trg_horse_to_oldinfo"))
            cx.execute(text("""
                CREATE TRIGGER trg_horse_to_oldinfo
                AFTER DELETE ON Horse
                FOR EACH ROW
                BEGIN
                  INSERT INTO old_info
                    (horseId, horseName, age, gender, registration, stableId, deleted_at)
                  VALUES
                    (OLD.horseId, OLD.horseName, OLD.age, OLD.gender, OLD.registration, OLD.stableId, NOW());
                END
            """))

# ---------- procedure ----------
        # 2) Stored procedure: delete owner + links; delete only horses that become unowned
        proc_exists = cx.execute(text("""
            SELECT COUNT(*) FROM information_schema.ROUTINES
            WHERE ROUTINE_SCHEMA = DATABASE()
              AND ROUTINE_TYPE   = 'PROCEDURE'
              AND ROUTINE_NAME   = 'delete_owner_and_related'
        """)).scalar()

        if not proc_exists:
            cx.execute(text("DROP PROCEDURE IF EXISTS delete_owner_and_related"))
            cx.execute(text("""
                CREATE PROCEDURE delete_owner_and_related(IN p_ownerId VARCHAR(15))
                BEGIN
                  START TRANSACTION;

                  -- Remove the owner's ownership links
                  DELETE FROM Owns WHERE ownerId = p_ownerId;

                  -- Horses that are now unowned (0 owners left)
                  CREATE TEMPORARY TABLE IF NOT EXISTS _to_delete (horseId VARCHAR(15) PRIMARY KEY);
                  DELETE FROM _to_delete;

                  INSERT INTO _to_delete (horseId)
                  SELECT h.horseId
                  FROM Horse h
                  LEFT JOIN Owns o ON o.horseId = h.horseId
                  GROUP BY h.horseId
                  HAVING COUNT(o.ownerId) = 0;

                  -- Remove related rows then the horse rows
                  DELETE FROM RaceResults WHERE horseId IN (SELECT horseId FROM _to_delete);
                  DELETE FROM Owns        WHERE horseId IN (SELECT horseId FROM _to_delete);
                  DELETE FROM Horse       WHERE horseId IN (SELECT horseId FROM _to_delete);

                  -- Finally remove the owner
                  DELETE FROM Owner WHERE ownerId = p_ownerId;

                  COMMIT;
                END
            """))

# Call this once when the app starts
ensure_db_programs()

def delete_owner_via_proc(owner_id: str):
    """Call the stored procedure that deletes the owner + related rows (safe)."""
    with ENGINE.begin() as cx:
        cx.execute(text("CALL delete_owner_and_related(:oid)"), {"oid": owner_id})


def render_delete_owner():
    st.markdown("#### 🧹 Delete an owner and all related information")
    if st.button("← Home"):
        go("home")
    # Load owners with a quick summary
    owners_df = q("""
        SELECT o.ownerId, o.fname, o.lname,
              COUNT(ow.horseId) AS horse_count
        FROM Owner o
        LEFT JOIN Owns ow ON ow.ownerId = o.ownerId
        GROUP BY o.ownerId, o.fname, o.lname
        ORDER BY o.fname, o.lname
    """)

    if owners_df.empty:
        st.info("No owners found.")
    else:
        # Build labels from ALL owners
        options = [
            (row.ownerId, f"{(row.fname or '').strip()} {(row.lname or '').strip()} "
                          f" - ({int(row.horse_count)} horse)")
            for _, row in owners_df.iterrows()
        ]

        # Prepare the dropdown list
        labels = [lab for _, lab in options]
        pick = st.selectbox("Owner", labels)
        owner_id = options[labels.index(pick)][0]

        # Show the horses linked to this owner (just for transparency)
        linked = q("""
            SELECT h.horseId, h.horseName,
                  (SELECT COUNT(*) FROM Owns o2 WHERE o2.horseId = h.horseId) AS owner_cnt
            FROM Owns ow
            JOIN Horse h ON h.horseId = ow.horseId
            WHERE ow.ownerId = :oid
            ORDER BY h.horseName
        """, {"oid": owner_id})
        st.caption("Horses linked to this owner (and how many total owners each horse has):")
        st.dataframe(linked, use_container_width=True)

        # Deletion behavior 
        # remove owner + links, and delete horses that become unowned
        confirm = st.checkbox(
            "I understand this will remove the owner and their ownership links; "
            "any horses with no owners left will also be deleted.",
            value=False
        )

        if st.button("Delete now", type="primary", disabled=not confirm):
          try:
              # 1) Call the stored procedure (this does everything safely)
              delete_owner_via_proc(owner_id)

              # 2) UI Reporter: Success message
              st.success(f"Owner **{owner_id}** was safely deleted.")

              # 3) trigger rerun after a brief moment (makes deleted owners dissaper)
              tm.sleep(5.0)  #  gives user 5 seconds to see the success banner
              st.rerun()

          except Exception as e:
              st.error(f"Delete failed: {e}")

# ---------------------------------------- Feature (3):  Delete an owner and all related info ----------------------------------------

def render_move_horse():
    st.markdown("#### ↔️ Move a horse from one stable to another")
    if st.button("← Home"):
        go("home")

    # Fetch data
    horses = q("""
        SELECT h.horseId, h.horseName, h.stableId AS current_stable, s.stableName AS current_stable_name
        FROM Horse h
        JOIN Stable s ON h.stableId = s.stableId
        ORDER BY h.horseName
    """)
    stables = q("SELECT stableId, stableName FROM Stable ORDER BY stableId")

    if horses.empty or stables.empty:
        st.warning("You must have horses and stables in the database to perform this action.")
        st.stop()

    # Dropdown: choose horse
    horse_labels = horses.apply(
        lambda r: f"{r['horseName']} [{r['horseId']} — current: {r['current_stable_name']}]",
        axis=1
    ).tolist()
    horse_choice = st.selectbox("Select a horse to move", horse_labels)
    chosen_horse = horses.iloc[horse_labels.index(horse_choice)]

    # Dropdown: choose destination stable (exclude current one)
    available_stables = stables[stables["stableId"] != chosen_horse["current_stable"]]
    dest_labels = available_stables.apply(
        lambda r: f"{r['stableName']} (#{r['stableId']})", axis=1
    ).tolist()
    new_stable_choice = st.selectbox("Select destination stable", dest_labels)
    new_stable = available_stables.iloc[dest_labels.index(new_stable_choice)]

    # Confirm and move
    if st.button("Move Horse", type="primary"):
        try:
            # 1) Validate that the destination is different
            if new_stable["stableId"] == chosen_horse["current_stable"]:
                st.error("The horse is already in this stable.")
            else:
                # 2) Perform the update
                with ENGINE.begin() as cx:
                    cx.execute(
                        text("""
                            UPDATE Horse
                            SET stableId = :newStable
                            WHERE horseId = :hid
                        """),
                        {"newStable": new_stable["stableId"], "hid": chosen_horse["horseId"]}
                    )

                # 3) Confirmation message
                st.success(
                    f"Horse **{chosen_horse['horseName']}** (#{chosen_horse['horseId']}) "
                    f"moved from **{chosen_horse['current_stable_name']}** "
                    f"to **{new_stable['stableName']}**."
                )
                tm.sleep(5.0)
                st.rerun()

        except Exception as e:
            st.error(f"Move failed: {e}")

# ---------------------------------------- Feature (4): Approve a new trainer to join a stable ----------------------------------------
# ---------- Applications Table ----------
def ensure_trainer_applications():
    """Create the TrainerApplications table (for pending approvals) if it does not exist."""
    with ENGINE.begin() as cx:
        cx.execute(text("""
            CREATE TABLE IF NOT EXISTS TrainerApplications (
              appId INT AUTO_INCREMENT PRIMARY KEY,
              fname VARCHAR(30) NOT NULL,
              lname VARCHAR(30) NOT NULL,
              stableId VARCHAR(30) NOT NULL,
              requestedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              status ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending',
              decidedAt DATETIME NULL,
              decisionBy VARCHAR(50) NULL,
              decisionReason TEXT NULL,
              approvedTrainerId VARCHAR(15) NULL,
              FOREIGN KEY (stableId) REFERENCES Stable(stableId)
            )
        """))


# ---------- Helper: new trainer ID generator ----------
def next_trainer_id() -> str:
    """Generate trainerNN based on current max."""
    df = q("""
        SELECT MAX(CAST(SUBSTRING(trainerId,8) AS UNSIGNED)) AS n
        FROM Trainer
        WHERE trainerId LIKE 'trainer%'
    """)
    n = int(df.iloc[0]["n"] or 0) + 1
    return f"trainer{n}"

# ---------- Seed a few pending applications once (FOR TESTING) ----------
def seed_pending_if_needed():
    """Insert a few pending rows if there are currently no pending applications."""
    with ENGINE.begin() as cx:
        # seed only if there are ZERO pending rows
        pending_cnt = cx.execute(
            text("SELECT COUNT(*) FROM TrainerApplications WHERE status='pending'")
        ).scalar()
        if int(pending_cnt or 0) > 0:
            return

        stables = cx.execute(
            text("SELECT stableId FROM Stable ORDER BY stableName LIMIT 5")
        ).mappings().all()
        if not stables:
            return

        from datetime import datetime, timedelta
        base_time = datetime.now()

        sample_data = [
            ("Ahmed", "Abed"),
            ("Faisal", "Hassan"),
            ("Mona", "Saeed"),
            ("Khalid", "Omar"),
            ("Sara", "Ali"),
        ]

        # insert up to the number of stables we have
        for i, ((fn, ln), st_row) in enumerate(zip(sample_data, stables)):
            ts = (base_time + timedelta(minutes=i * 10)).strftime("%Y-%m-%d %H:%M:%S")
            cx.execute(
                text("""
                    INSERT INTO TrainerApplications (fname, lname, stableId, requestedAt)
                    VALUES (:fn, :ln, :sid, :ts)
                """),
                {"fn": fn, "ln": ln, "sid": st_row["stableId"], "ts": ts},
            )

def render_approve_trainer():
    st.markdown("#### ✅ Approve a new trainer to join a stable")
    if st.button("← Home"):
        go("home")

    ensure_trainer_applications()
    seed_pending_if_needed()

    # ---------- Load pending applications ----------
    pending_apps = q("""
        SELECT ta.appId, ta.fname, ta.lname, ta.stableId, s.stableName, ta.requestedAt
        FROM TrainerApplications ta
        JOIN Stable s ON s.stableId = ta.stableId
        WHERE ta.status = 'pending'
        ORDER BY ta.requestedAt DESC  
    """)

    if pending_apps.empty:
        st.info("No pending trainer applications found.")

    else:
        st.dataframe(pending_apps, use_container_width=True)

        app_labels = pending_apps.apply(
            lambda r: f"[App #{r['appId']}] {r['fname']} {r['lname']} — requested {r['stableName']} ({r['stableId']})",
            axis=1
        ).tolist()
        choice = st.selectbox("Select an application to review", app_labels)
        selected = pending_apps.iloc[app_labels.index(choice)]

        st.markdown(f"### Reviewing Application #{selected['appId']}")
        st.write(f"**Name:** {selected['fname']} {selected['lname']}")
        st.write(f"**Requested Stable:** {selected['stableName']} (#{selected['stableId']})")
        st.write(f"**Requested At:** {selected['requestedAt']}")

        new_tid = next_trainer_id()
        st.write(f"**Auto-generated Trainer ID:** `{new_tid}`")

        c1, c2 = st.columns(2)

       # --- Approve ---
        with c1:
            if st.button("Approve Trainer", type="primary"):
                try:
                    with ENGINE.begin() as cx:
                        cx.execute(text("""
                            INSERT INTO Trainer (trainerId, lname, fname, stableId)
                            VALUES (:tid, :ln, :fn, :sid)
                        """), {
                            "tid": new_tid,
                            "ln": selected["lname"],
                            "fn": selected["fname"],
                            "sid": selected["stableId"],
                        })
                        cx.execute(text("""
                            UPDATE TrainerApplications
                            SET status='approved', decidedAt=NOW(),
                                decisionBy='Admin', approvedTrainerId=:tid
                            WHERE appId=:id
                        """), {"tid": new_tid, "id": selected["appId"]})

                    st.success(
                        f"Trainer **{selected['fname']} {selected['lname']}** approved into "
                        f"**{selected['stableName']}** as `{new_tid}`."
                    )
                    tm.sleep(3)
                    st.rerun()
                except Exception as e:
                    st.error(f"Approval failed: {e}")

        # --- Reject ---
        with c2:
            reject_click = st.button("Reject Trainer")
            if reject_click:
                try:
                    with ENGINE.begin() as cx:
                        cx.execute(text("""
                            UPDATE TrainerApplications
                            SET status='rejected', decidedAt=NOW(),
                                decisionBy='Admin', decisionReason=:rsn
                            WHERE appId=:id
                        """))

                    st.success(
                        f"Application for **{selected['fname']} {selected['lname']}** rejected. "
                    )
                    tm.sleep(3)
                    st.rerun()
                except Exception as e:
                    st.error(f"Rejection failed: {e}")

# ------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- GUEST --------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------- Feature (1): Horses Owned by a Specific Person -------------------------------------------
def render_g_horses_by_owner():
    backbar("guest_home")  
    st.subheader("🔎 Horses by Owner")
    st.caption("Browse horse names, ages, and trainer names by owner's last name (lname).")

    with st.form("f_owner", clear_on_submit=False):
        lname = st.text_input("Owner last name", placeholder="e.g., Ahmed")
        submitted = st.form_submit_button("Search", use_container_width=True)

    if not submitted:
        return

    term = (lname or "").strip()
    if not term:
        st.warning("Please enter a last name to search.")
        return

    try:
        # Combine multiple trainers (same stable can have many) into one cell per horse
        df = q("""
            SELECT
                h.horseName AS `Horse`,
                h.age       AS `Age`,
                COALESCE(GROUP_CONCAT(DISTINCT CONCAT(t.fname, ' ', t.lname)
                         ORDER BY t.lname SEPARATOR ', '), '—') AS `Trainer(s)`
            FROM Owner o
            JOIN Owns   ow ON ow.ownerId = o.ownerId
            JOIN Horse   h ON h.horseId  = ow.horseId
            LEFT JOIN Trainer t ON t.stableId = h.stableId
            WHERE o.lname LIKE :pat
            GROUP BY h.horseId, h.horseName, h.age
            ORDER BY h.horseName
        """, {"pat": f"%{term}%"})

        if df.empty:
            st.info("No horses found for that last name.")
        else:
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Search failed: {e}")

# ------------------------------------- Feature (2): Trainers Who Have Trained Winning Horses ---------------------------------------
def render_g_trainer_winners():
    backbar("guest_home")
    st.subheader("🏅 Winning Trainers")
    st.caption("List trainers who trained horses that won first place.")

    sql = """
        SELECT 
            t.fname     AS `Trainer First`,
            t.lname     AS `Trainer Last`,
            h.horseName AS `Winning Horse`,
            r.raceName  AS `Race Name`,
            r.raceDate  AS `Race Date`,
            r.trackName AS `Track`
        FROM RaceResults rr
        JOIN Horse   h ON h.horseId = rr.horseId
        JOIN Trainer t ON t.stableId = h.stableId
        JOIN Race    r ON r.raceId   = rr.raceId
        WHERE rr.results = 'first'
        ORDER BY r.raceDate DESC, t.lname, t.fname;
    """
    df = q(sql)
    if df.empty:
        st.info("No winning trainers found.")
    else:
        st.dataframe(df, use_container_width=True)

# ------------------------------------------- Feature (3): Total Winnings per Trainer -------------------------------------------
def render_g_trainer_winnings():
    backbar("guest_home")
    st.subheader("💰 Trainer Winnings")
    st.caption("Show total prize money per trainer, sorted in descending order.")

    if st.button("Calculate", use_container_width=True):
        sql = """
            SELECT 
                CONCAT(t.fname, ' ', t.lname) AS `Trainer`,
                COALESCE(SUM(rr.prize), 0)    AS `Total Winnings`
            FROM Trainer t
            LEFT JOIN Horse       h  ON h.stableId = t.stableId
            LEFT JOIN RaceResults rr ON rr.horseId  = h.horseId
            GROUP BY t.trainerId, t.fname, t.lname
            ORDER BY `Total Winnings` DESC;
        """
        df = q(sql)
        if df.empty:
            st.info("No trainer winnings found.")
        else:
            st.dataframe(df, use_container_width=True)

# ------------------------------------------- Feature (4): Race Statistics per Track -------------------------------------------
def render_g_track_stats():
  backbar("guest_home")
  st.subheader("🏟️ Track Insights")
  st.caption("View the number of races and horse participations per track.")

  if st.button("Show stats", use_container_width=True):
      sql = """
          SELECT
              r.trackName               AS `Track`,
              COUNT(DISTINCT r.raceId)  AS `Number of Races`,
              COUNT(rr.horseId)         AS `Total Horses Participating`
          FROM Race r
          LEFT JOIN RaceResults rr ON rr.raceId = r.raceId
          GROUP BY r.trackName
          ORDER BY `Number of Races` DESC, r.trackName;
      """
      df = q(sql)
      if df.empty:
          st.info("No track statistics found.")
      else:
          st.dataframe(df, use_container_width=True)


# ------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- Router -------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
if st.session_state.role == "Admin":
    if st.session_state.view == "home":
        admin_home()
    elif st.session_state.view == "add_race":
        render_add_race()
    elif st.session_state.view == "delete_owner":
        render_delete_owner()
    elif st.session_state.view == "move_horse":
        render_move_horse()
    elif st.session_state.view == "approve_trainer":
        render_approve_trainer()
else:  # Guest
    if st.session_state.view not in {"guest_home", "g_owners_horses", "g_trainer_winners", "g_trainer_winnings", "g_track_stats"}:
        st.session_state.view = "guest_home"

    if st.session_state.view == "guest_home":
        guest_home()
    elif st.session_state.view == "g_owners_horses":
        render_g_horses_by_owner()
    elif st.session_state.view == "g_trainer_winners":
        render_g_trainer_winners()
    elif st.session_state.view == "g_trainer_winnings":
        render_g_trainer_winnings()
    elif st.session_state.view == "g_track_stats":
        render_g_track_stats()