from datetime import datetime
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.entities import (
    Department, Room, Faculty, Course, StudentCohort,
    TimetableSchedule, Disruption, AuditLog
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if data already exists
    if db.query(Department).first():
        db.close()
        return

    print("Seeding Nexora Campus realistic Indian University data...")

    # 1. Departments
    depts = [
        Department(code="CSE", name="Computer Science & Engineering", building="Ramanujan Computing Complex"),
        Department(code="AI-DS", name="Artificial Intelligence & Data Science", building="Turing Centre of Excellence"),
        Department(code="ECE", name="Electronics & Communication Engineering", building="Aryabhata Academic Block"),
        Department(code="MECH", name="Mechanical & Automation Engineering", building="Vikram Sarabhai Innovation Tower"),
    ]
    db.add_all(depts)
    db.commit()

    dept_cse = db.query(Department).filter_by(code="CSE").first()
    dept_aids = db.query(Department).filter_by(code="AI-DS").first()
    dept_ece = db.query(Department).filter_by(code="ECE").first()
    dept_mech = db.query(Department).filter_by(code="MECH").first()

    # 2. Rooms
    rooms = [
        # AI Lab 01 - The Target Disrupted Lab
        Room(
            code="AI-LAB-01",
            name="Artificial Intelligence Lab 01",
            capacity=40,
            room_type="Computer Lab",
            building="Turing Centre of Excellence",
            floor=2,
            equipment=["GPU Workstations", "Smart Projector", "High-Speed LAN", "Audio System"],
            is_available=True,
            maintenance_notes=None
        ),
        # Suitable Alternative 1: Same building, same type, matching GPU equipment, capacity 42 >= 36
        Room(
            code="AI-LAB-02",
            name="Data Science & NLP Lab",
            capacity=42,
            room_type="Computer Lab",
            building="Turing Centre of Excellence",
            floor=2,
            equipment=["GPU Workstations", "Smart Projector", "High-Speed LAN", "Audio System"],
            is_available=True,
            maintenance_notes=None
        ),
        # Suitable Alternative 2: Adjacent RCC block, matching GPU equipment, capacity 45 >= 36
        Room(
            code="CS-LAB-03",
            name="Advanced Computing & Cloud Lab",
            capacity=45,
            room_type="Computer Lab",
            building="Ramanujan Computing Complex",
            floor=1,
            equipment=["GPU Workstations", "Smart Projector", "High-Speed LAN", "Audio System"],
            is_available=True,
            maintenance_notes=None
        ),
        # Occupied Alternative: Has GPU workstations, but scheduled with another course on Monday 09:00-11:00
        Room(
            code="CS-LAB-02",
            name="Web Technologies & Systems Lab",
            capacity=40,
            room_type="Computer Lab",
            building="Ramanujan Computing Complex",
            floor=2,
            equipment=["GPU Workstations", "Smart Projector", "High-Speed LAN"],
            is_available=True,
            maintenance_notes=None
        ),
        # Unsuitable Alternative 1: Missing GPU equipment (Only Standard PCs)
        Room(
            code="CS-LAB-01",
            name="Basic Programming Lab",
            capacity=50,
            room_type="Computer Lab",
            building="Ramanujan Computing Complex",
            floor=1,
            equipment=["Standard PCs", "Projector", "High-Speed LAN"],
            is_available=True,
            maintenance_notes=None
        ),
        # Unsuitable Alternative 2: Capacity too small (Capacity 30 < 36 students)
        Room(
            code="CLASS-302",
            name="Smart Seminar Classroom 302",
            capacity=30,
            room_type="Classroom",
            building="Aryabhata Academic Block",
            floor=3,
            equipment=["Projector", "Whiteboard", "High-Speed LAN"],
            is_available=True,
            maintenance_notes=None
        ),
        # Unsuitable Alternative 3: Wrong room type (Seminar Hall, no desktop workstations)
        Room(
            code="SEMINAR-HALL-A",
            name="Sir C.V. Raman Auditorium",
            capacity=120,
            room_type="Seminar Hall",
            building="Aryabhata Academic Block",
            floor=1,
            equipment=["Smart Projector", "Surround Audio", "Podium Mic", "Stage Lighting"],
            is_available=True,
            maintenance_notes=None
        ),
        # Additional campus rooms
        Room(
            code="LH-101",
            name="Turing Lecture Hall 101",
            capacity=75,
            room_type="Lecture Hall",
            building="Turing Centre of Excellence",
            floor=1,
            equipment=["Smart Board", "Projector", "Audio System"],
            is_available=True,
            maintenance_notes=None
        ),
        Room(
            code="LH-201",
            name="Ramanujan Lecture Theatre",
            capacity=90,
            room_type="Lecture Hall",
            building="Ramanujan Computing Complex",
            floor=2,
            equipment=["Smart Board", "Projector", "Audio System", "Tiered Seating"],
            is_available=True,
            maintenance_notes=None
        ),
        Room(
            code="IOT-LAB-01",
            name="Embedded Systems & IoT Lab",
            capacity=35,
            room_type="Hardware Lab",
            building="Aryabhata Academic Block",
            floor=2,
            equipment=["Oscilloscopes", "Soldering Stations", "Microcontroller Kits", "Logic Analyzers"],
            is_available=True,
            maintenance_notes=None
        ),
        Room(
            code="ROBOTICS-LAB",
            name="Autonomous Robotics Lab",
            capacity=30,
            room_type="Robotics Lab",
            building="Vikram Sarabhai Innovation Tower",
            floor=1,
            equipment=["Robotic Arms", "Lidar Sensors", "Workstations", "3D Printers"],
            is_available=True,
            maintenance_notes=None
        )
    ]
    db.add_all(rooms)
    db.commit()

    # 3. Faculties
    faculties = [
        Faculty(name="Dr. Priya Sharma", email="priya.sharma@nexora.edu.in", department_id=dept_aids.id, designation="Associate Professor"),
        Faculty(name="Prof. Rajesh Verma", email="rajesh.verma@nexora.edu.in", department_id=dept_cse.id, designation="Professor & HOD"),
        Faculty(name="Dr. Ananya Iyer", email="ananya.iyer@nexora.edu.in", department_id=dept_aids.id, designation="Assistant Professor"),
        Faculty(name="Dr. Vikram Sengupta", email="vikram.sengupta@nexora.edu.in", department_id=dept_ece.id, designation="Associate Professor"),
        Faculty(name="Prof. Arun Swaminathan", email="arun.swami@nexora.edu.in", department_id=dept_cse.id, designation="Professor"),
        Faculty(name="Dr. Meera Nambiar", email="meera.nambiar@nexora.edu.in", department_id=dept_mech.id, designation="Assistant Professor"),
    ]
    db.add_all(faculties)
    db.commit()

    # 4. Student Cohorts
    cohorts = [
        StudentCohort(code="BTECH-AIDS-V", name="B.Tech AI & Data Science - Sem 5", department_id=dept_aids.id, size=36, semester=5),
        StudentCohort(code="BTECH-CSE-V-A", name="B.Tech Computer Science - Sem 5 Sec A", department_id=dept_cse.id, size=42, semester=5),
        StudentCohort(code="BTECH-CSE-VII", name="B.Tech Computer Science - Sem 7", department_id=dept_cse.id, size=38, semester=7),
        StudentCohort(code="BTECH-ECE-V", name="B.Tech Electronics & Comm - Sem 5", department_id=dept_ece.id, size=34, semester=5),
        StudentCohort(code="MTECH-AI-I", name="M.Tech Artificial Intelligence - Sem 1", department_id=dept_aids.id, size=24, semester=1),
    ]
    db.add_all(cohorts)
    db.commit()

    # 5. Courses
    courses = [
        Course(
            code="AI501-LAB",
            name="Deep Learning & Neural Networks Practical",
            department_id=dept_aids.id,
            credits=2,
            required_room_type="Computer Lab",
            required_equipment=["GPU Workstations", "High-Speed LAN"],
            semester=5
        ),
        Course(
            code="CS503-LAB",
            name="Full-Stack Web Architectures Lab",
            department_id=dept_cse.id,
            credits=2,
            required_room_type="Computer Lab",
            required_equipment=["GPU Workstations", "High-Speed LAN"],
            semester=5
        ),
        Course(
            code="CS701-LAB",
            name="Cloud Computing & Distributed Systems Lab",
            department_id=dept_cse.id,
            credits=2,
            required_room_type="Computer Lab",
            required_equipment=["High-Speed LAN"],
            semester=7
        ),
        Course(
            code="AI502-TH",
            name="Statistical Machine Learning Theory",
            department_id=dept_aids.id,
            credits=3,
            required_room_type="Lecture Hall",
            required_equipment=["Smart Board", "Projector"],
            semester=5
        ),
        Course(
            code="EC504-LAB",
            name="Embedded Systems Design Lab",
            department_id=dept_ece.id,
            credits=2,
            required_room_type="Hardware Lab",
            required_equipment=["Oscilloscopes", "Microcontroller Kits"],
            semester=5
        ),
    ]
    db.add_all(courses)
    db.commit()

    # Query objects for schedule creation
    r_ai01 = db.query(Room).filter_by(code="AI-LAB-01").first()
    r_ai02 = db.query(Room).filter_by(code="AI-LAB-02").first()
    r_cs03 = db.query(Room).filter_by(code="CS-LAB-03").first()
    r_cs02 = db.query(Room).filter_by(code="CS-LAB-02").first()
    r_lh101 = db.query(Room).filter_by(code="LH-101").first()
    r_lh201 = db.query(Room).filter_by(code="LH-201").first()
    r_iot01 = db.query(Room).filter_by(code="IOT-LAB-01").first()

    f_priya = db.query(Faculty).filter_by(name="Dr. Priya Sharma").first()
    f_rajesh = db.query(Faculty).filter_by(name="Prof. Rajesh Verma").first()
    f_ananya = db.query(Faculty).filter_by(name="Dr. Ananya Iyer").first()
    f_vikram = db.query(Faculty).filter_by(name="Dr. Vikram Sengupta").first()
    f_arun = db.query(Faculty).filter_by(name="Prof. Arun Swaminathan").first()

    c_aids_v = db.query(StudentCohort).filter_by(code="BTECH-AIDS-V").first()
    c_cse_va = db.query(StudentCohort).filter_by(code="BTECH-CSE-V-A").first()
    c_cse_vii = db.query(StudentCohort).filter_by(code="BTECH-CSE-VII").first()
    c_ece_v = db.query(StudentCohort).filter_by(code="BTECH-ECE-V").first()

    co_ai501 = db.query(Course).filter_by(code="AI501-LAB").first()
    co_cs503 = db.query(Course).filter_by(code="CS503-LAB").first()
    co_cs701 = db.query(Course).filter_by(code="CS701-LAB").first()
    co_ai502 = db.query(Course).filter_by(code="AI502-TH").first()
    co_ec504 = db.query(Course).filter_by(code="EC504-LAB").first()

    # 6. Schedules
    schedules = [
        # *** The Main Target Class ***
        # Monday 09:00 - 11:00 in AI-LAB-01
        TimetableSchedule(
            course_id=co_ai501.id,
            faculty_id=f_priya.id,
            cohort_id=c_aids_v.id,
            room_id=r_ai01.id,
            day_of_week="Monday",
            start_time="09:00",
            end_time="11:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
        # Conflicting class in CS-LAB-02 (Monday 09:00 - 11:00)
        # Prevents CS-LAB-02 from being chosen because room is occupied!
        TimetableSchedule(
            course_id=co_cs503.id,
            faculty_id=f_rajesh.id,
            cohort_id=c_cse_va.id,
            room_id=r_cs02.id,
            day_of_week="Monday",
            start_time="09:00",
            end_time="11:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
        # Monday 11:30 - 13:00 - BTECH-AIDS-V has lecture with Dr. Priya Sharma in LH-101
        # Shows faculty and cohort busy later in the day
        TimetableSchedule(
            course_id=co_ai502.id,
            faculty_id=f_priya.id,
            cohort_id=c_aids_v.id,
            room_id=r_lh101.id,
            day_of_week="Monday",
            start_time="11:30",
            end_time="13:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
        # Monday 09:00 - 11:00 - ECE Cohort in IoT Lab
        TimetableSchedule(
            course_id=co_ec504.id,
            faculty_id=f_vikram.id,
            cohort_id=c_ece_v.id,
            room_id=r_iot01.id,
            day_of_week="Monday",
            start_time="09:00",
            end_time="11:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
        # Tuesday 09:00 - 11:00 - AI-LAB-01 class
        TimetableSchedule(
            course_id=co_cs701.id,
            faculty_id=f_arun.id,
            cohort_id=c_cse_vii.id,
            room_id=r_ai01.id,
            day_of_week="Tuesday",
            start_time="09:00",
            end_time="11:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
        # Wednesday 10:00 - 12:00
        TimetableSchedule(
            course_id=co_ai501.id,
            faculty_id=f_priya.id,
            cohort_id=c_aids_v.id,
            room_id=r_ai02.id,
            day_of_week="Wednesday",
            start_time="10:00",
            end_time="12:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
        # Thursday 14:00 - 16:00
        TimetableSchedule(
            course_id=co_cs503.id,
            faculty_id=f_rajesh.id,
            cohort_id=c_cse_va.id,
            room_id=r_cs03.id,
            day_of_week="Thursday",
            start_time="14:00",
            end_time="16:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
        # Friday 11:00 - 13:00
        TimetableSchedule(
            course_id=co_ai502.id,
            faculty_id=f_ananya.id,
            cohort_id=c_aids_v.id,
            room_id=r_lh201.id,
            day_of_week="Friday",
            start_time="11:00",
            end_time="13:00",
            status="Scheduled",
            academic_term="Fall 2026"
        ),
    ]
    db.add_all(schedules)
    db.commit()

    # 7. Audit log for initial system setup
    audit = AuditLog(
        entity_type="System",
        entity_id=1,
        action="INITIALIZE",
        details={"message": "Nexora Campus database initialized with realistic seed dataset."},
        actor="System",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    db.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
