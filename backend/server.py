from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone, timedelta


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")


class Employee(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    daily_salary: float
    project_id: Optional[str] = None
    trade: Optional[str] = None
    created_at: str
    is_active: bool = True


class EmployeeCreate(BaseModel):
    name: str
    daily_salary: float
    project_id: Optional[str] = None
    trade: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    daily_salary: Optional[float] = None
    project_id: Optional[str] = None
    trade: Optional[str] = None
    is_active: Optional[bool] = None


class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    description: Optional[str] = ""
    start_date: str
    is_active: bool = True
    created_at: str


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    start_date: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    is_active: Optional[bool] = None


class Contractor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    weekly_payment: float
    project_name: str
    budget: float
    total_paid: float = 0.0
    remaining_balance: float = 0.0
    created_at: str
    is_active: bool = True


class ContractorCreate(BaseModel):
    name: str
    weekly_payment: float
    project_name: str
    budget: float


class ContractorUpdate(BaseModel):
    name: Optional[str] = None
    weekly_payment: Optional[float] = None
    project_name: Optional[str] = None
    budget: Optional[float] = None
    is_active: Optional[bool] = None


class Attendance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    employee_id: str
    date: str
    status: str
    late_hours: float = 0.0
    week_start_date: str


class AttendanceCreate(BaseModel):
    employee_id: str
    date: str
    status: str
    late_hours: float = 0.0
    week_start_date: str


class Advance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    employee_id: str
    amount: float
    date: str
    description: Optional[str] = ""
    week_start_date: str


class AdvanceCreate(BaseModel):
    employee_id: str
    amount: float
    date: str
    description: Optional[str] = ""
    week_start_date: str


class ContractorCertification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    contractor_id: str
    week_start_date: str
    amount: float
    description: Optional[str] = ""
    created_at: str


class ContractorCertificationCreate(BaseModel):
    contractor_id: str
    week_start_date: str
    amount: float
    description: Optional[str] = ""


class PaymentHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    employee_id: str
    week_start_date: str
    days_worked: int
    total_salary: float
    total_advances: float
    net_payment: float
    paid_at: str


class PaymentCalculation(BaseModel):
    week_start_date: str


class DashboardStats(BaseModel):
    total_employees: int
    active_employees: int
    total_contractors: int
    active_contractors: int
    total_payment_this_week: float
    contractors_payment_this_week: float
    total_advances_this_week: float
    net_payment_this_week: float
    total_to_pay_friday: float


@api_router.get("/")
async def root():
    return {"message": "PayrollPro API"}


@api_router.post("/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate):
    from uuid import uuid4
    employee_dict = employee.model_dump()
    employee_obj = Employee(
        id=str(uuid4()),
        name=employee_dict['name'],
        daily_salary=employee_dict['daily_salary'],
        project_id=employee_dict.get('project_id'),
        trade=employee_dict.get('trade'),
        created_at=datetime.now(timezone.utc).isoformat(),
        is_active=True
    )
    doc = employee_obj.model_dump()
    await db.employees.insert_one(doc)
    return employee_obj


@api_router.get("/employees", response_model=List[Employee])
async def get_employees():
    employees = await db.employees.find({}, {"_id": 0}).to_list(1000)
    return employees


@api_router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@api_router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, update_data: EmployeeUpdate):
    employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        await db.employees.update_one({"id": employee_id}, {"$set": update_dict})
    
    updated_employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    return updated_employee


@api_router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    result = await db.employees.delete_one({"id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    from uuid import uuid4
    project_dict = project.model_dump()
    project_obj = Project(
        id=str(uuid4()),
        name=project_dict['name'],
        description=project_dict.get('description', ''),
        start_date=project_dict['start_date'],
        is_active=True,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    doc = project_obj.model_dump()
    await db.projects.insert_one(doc)
    return project_obj


@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find({}, {"_id": 0}).to_list(1000)
    return projects


@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, update_data: ProjectUpdate):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        await db.projects.update_one({"id": project_id}, {"$set": update_dict})
    
    updated_project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return updated_project


@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


@api_router.post("/contractors", response_model=Contractor)
async def create_contractor(contractor: ContractorCreate):
    from uuid import uuid4
    contractor_dict = contractor.model_dump()
    contractor_obj = Contractor(
        id=str(uuid4()),
        name=contractor_dict['name'],
        weekly_payment=contractor_dict['weekly_payment'],
        project_name=contractor_dict['project_name'],
        budget=contractor_dict['budget'],
        total_paid=0.0,
        remaining_balance=contractor_dict['budget'],
        created_at=datetime.now(timezone.utc).isoformat(),
        is_active=True
    )
    doc = contractor_obj.model_dump()
    await db.contractors.insert_one(doc)
    return contractor_obj


@api_router.get("/contractors", response_model=List[Contractor])
async def get_contractors():
    contractors = await db.contractors.find({}, {"_id": 0}).to_list(1000)
    for contractor in contractors:
        budget = contractor.get('budget', 0)
        total_paid = contractor.get('total_paid', 0)
        contractor['budget'] = budget
        contractor['total_paid'] = total_paid
        contractor['remaining_balance'] = budget - total_paid
        if 'project_name' not in contractor:
            contractor['project_name'] = 'Sin asignar'
    return contractors


@api_router.get("/contractors/{contractor_id}", response_model=Contractor)
async def get_contractor(contractor_id: str):
    contractor = await db.contractors.find_one({"id": contractor_id}, {"_id": 0})
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    budget = contractor.get('budget', 0)
    total_paid = contractor.get('total_paid', 0)
    contractor['budget'] = budget
    contractor['total_paid'] = total_paid
    contractor['remaining_balance'] = budget - total_paid
    if 'project_name' not in contractor:
        contractor['project_name'] = 'Sin asignar'
    return contractor


@api_router.put("/contractors/{contractor_id}", response_model=Contractor)
async def update_contractor(contractor_id: str, update_data: ContractorUpdate):
    contractor = await db.contractors.find_one({"id": contractor_id}, {"_id": 0})
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        await db.contractors.update_one({"id": contractor_id}, {"$set": update_dict})
    
    updated_contractor = await db.contractors.find_one({"id": contractor_id}, {"_id": 0})
    budget = updated_contractor.get('budget', 0)
    total_paid = updated_contractor.get('total_paid', 0)
    updated_contractor['budget'] = budget
    updated_contractor['total_paid'] = total_paid
    updated_contractor['remaining_balance'] = budget - total_paid
    if 'project_name' not in updated_contractor:
        updated_contractor['project_name'] = 'Sin asignar'
    return updated_contractor


@api_router.delete("/contractors/{contractor_id}")
async def delete_contractor(contractor_id: str):
    result = await db.contractors.delete_one({"id": contractor_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contractor not found")
    return {"message": "Contractor deleted successfully"}


@api_router.post("/attendance", response_model=Attendance)
async def create_attendance(attendance: AttendanceCreate):
    from uuid import uuid4
    attendance_dict = attendance.model_dump()
    
    existing = await db.attendance.find_one({
        "employee_id": attendance_dict['employee_id'],
        "date": attendance_dict['date']
    })
    
    if existing:
        update_data = {
            "status": attendance_dict['status'],
            "late_hours": attendance_dict.get('late_hours', 0.0)
        }
        await db.attendance.update_one(
            {"employee_id": attendance_dict['employee_id'], "date": attendance_dict['date']},
            {"$set": update_data}
        )
        updated = await db.attendance.find_one(
            {"employee_id": attendance_dict['employee_id'], "date": attendance_dict['date']},
            {"_id": 0}
        )
        if 'late_hours' not in updated:
            updated['late_hours'] = 0.0
        return updated
    
    attendance_obj = Attendance(
        id=str(uuid4()),
        employee_id=attendance_dict['employee_id'],
        date=attendance_dict['date'],
        status=attendance_dict['status'],
        late_hours=attendance_dict.get('late_hours', 0.0),
        week_start_date=attendance_dict['week_start_date']
    )
    doc = attendance_obj.model_dump()
    await db.attendance.insert_one(doc)
    return attendance_obj


@api_router.get("/attendance", response_model=List[Attendance])
async def get_attendance():
    attendance = await db.attendance.find({}, {"_id": 0}).to_list(5000)
    for record in attendance:
        if 'late_hours' not in record:
            record['late_hours'] = 0.0
    return attendance


@api_router.get("/attendance/week/{week_start}", response_model=List[Attendance])
async def get_week_attendance(week_start: str):
    attendance = await db.attendance.find({"week_start_date": week_start}, {"_id": 0}).to_list(5000)
    for record in attendance:
        if 'late_hours' not in record:
            record['late_hours'] = 0.0
    return attendance


@api_router.post("/advances", response_model=Advance)
async def create_advance(advance: AdvanceCreate):
    from uuid import uuid4
    advance_dict = advance.model_dump()
    advance_obj = Advance(
        id=str(uuid4()),
        employee_id=advance_dict['employee_id'],
        amount=advance_dict['amount'],
        date=advance_dict['date'],
        description=advance_dict.get('description', ''),
        week_start_date=advance_dict['week_start_date']
    )
    doc = advance_obj.model_dump()
    await db.advances.insert_one(doc)
    return advance_obj


@api_router.get("/advances", response_model=List[Advance])
async def get_advances():
    advances = await db.advances.find({}, {"_id": 0}).to_list(5000)
    return advances


@api_router.get("/advances/employee/{employee_id}", response_model=List[Advance])
async def get_employee_advances(employee_id: str):
    advances = await db.advances.find({"employee_id": employee_id}, {"_id": 0}).to_list(1000)
    return advances


@api_router.delete("/advances/{advance_id}")
async def delete_advance(advance_id: str):
    result = await db.advances.delete_one({"id": advance_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Advance not found")
    return {"message": "Advance deleted successfully"}


@api_router.post("/payments/calculate")
async def calculate_payments(calculation: PaymentCalculation):
    from uuid import uuid4
    week_start = calculation.week_start_date
    
    employees = await db.employees.find({"is_active": True}, {"_id": 0}).to_list(1000)
    contractors = await db.contractors.find({"is_active": True}, {"_id": 0}).to_list(1000)
    attendance_records = await db.attendance.find({"week_start_date": week_start}, {"_id": 0}).to_list(5000)
    advances_records = await db.advances.find({"week_start_date": week_start}, {"_id": 0}).to_list(5000)
    
    payment_records = []
    
    for employee in employees:
        employee_attendance = [a for a in attendance_records if a['employee_id'] == employee['id']]
        days_worked = sum(1 for a in employee_attendance if a['status'] in ['present', 'late'])
        
        # Calcular descuento por horas tarde
        total_late_hours = sum(a.get('late_hours', 0) for a in employee_attendance if a['status'] == 'late')
        hourly_rate = employee['daily_salary'] / 8  # Jornada de 8 horas
        late_discount = total_late_hours * hourly_rate
        
        employee_advances = [a for a in advances_records if a['employee_id'] == employee['id']]
        total_advances = sum(a['amount'] for a in employee_advances)
        
        total_salary = (days_worked * employee['daily_salary']) - late_discount
        net_payment = total_salary - total_advances
        
        payment_obj = PaymentHistory(
            id=str(uuid4()),
            employee_id=employee['id'],
            week_start_date=week_start,
            days_worked=days_worked,
            total_salary=total_salary,
            total_advances=total_advances,
            net_payment=net_payment,
            paid_at=datetime.now(timezone.utc).isoformat()
        )
        
        doc = payment_obj.model_dump()
        await db.payment_history.insert_one(doc)
        payment_records.append(doc)
    
    for contractor in contractors:
        new_total_paid = contractor.get('total_paid', 0) + contractor['weekly_payment']
        await db.contractors.update_one(
            {"id": contractor['id']},
            {"$set": {"total_paid": new_total_paid}}
        )
    
    return {
        "message": "Payments calculated successfully", 
        "count": len(payment_records),
        "contractors_updated": len(contractors)
    }


# Contractor Certifications endpoints
@api_router.post("/certifications", response_model=ContractorCertification)
async def create_certification(certification: ContractorCertificationCreate):
    from uuid import uuid4
    
    # Verify contractor exists
    contractor = await db.contractors.find_one({"id": certification.contractor_id}, {"_id": 0})
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    
    certification_dict = certification.model_dump()
    certification_obj = ContractorCertification(
        id=str(uuid4()),
        contractor_id=certification_dict['contractor_id'],
        week_start_date=certification_dict['week_start_date'],
        amount=certification_dict['amount'],
        description=certification_dict.get('description', ''),
        created_at=datetime.now(timezone.utc).isoformat()
    )
    doc = certification_obj.model_dump()
    await db.certifications.insert_one(doc)
    
    # Update contractor's total_paid
    new_total_paid = contractor.get('total_paid', 0) + certification_dict['amount']
    await db.contractors.update_one(
        {"id": certification.contractor_id},
        {"$set": {"total_paid": new_total_paid}}
    )
    
    return certification_obj


@api_router.get("/certifications", response_model=List[ContractorCertification])
async def get_all_certifications():
    certifications = await db.certifications.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
    return certifications


@api_router.get("/certifications/contractor/{contractor_id}", response_model=List[ContractorCertification])
async def get_contractor_certifications(contractor_id: str):
    certifications = await db.certifications.find(
        {"contractor_id": contractor_id}, 
        {"_id": 0}
    ).sort("week_start_date", -1).to_list(1000)
    return certifications


@api_router.delete("/certifications/{certification_id}")
async def delete_certification(certification_id: str):
    # Get certification to know the amount to subtract
    certification = await db.certifications.find_one({"id": certification_id}, {"_id": 0})
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    # Update contractor's total_paid
    contractor = await db.contractors.find_one({"id": certification['contractor_id']}, {"_id": 0})
    if contractor:
        new_total_paid = max(0, contractor.get('total_paid', 0) - certification['amount'])
        await db.contractors.update_one(
            {"id": certification['contractor_id']},
            {"$set": {"total_paid": new_total_paid}}
        )
    
    result = await db.certifications.delete_one({"id": certification_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"message": "Certification deleted successfully"}


@api_router.get("/payments/history", response_model=List[PaymentHistory])
async def get_payment_history():
    payments = await db.payment_history.find({}, {"_id": 0}).sort("paid_at", -1).to_list(1000)
    return payments


@api_router.get("/payments/by-project/{week_start}")
async def get_payments_by_project(week_start: str):
    employees = await db.employees.find({"is_active": True}, {"_id": 0}).to_list(1000)
    projects = await db.projects.find({}, {"_id": 0}).to_list(1000)
    attendance_records = await db.attendance.find({"week_start_date": week_start}, {"_id": 0}).to_list(5000)
    advances_records = await db.advances.find({"week_start_date": week_start}, {"_id": 0}).to_list(5000)
    
    project_payments = {}
    
    for project in projects:
        project_employees = [e for e in employees if e.get('project_id') == project['id']]
        
        trade_totals = {}
        project_total = 0
        
        for employee in project_employees:
            employee_attendance = [a for a in attendance_records if a['employee_id'] == employee['id']]
            days_worked = sum(1 for a in employee_attendance if a['status'] in ['present', 'late'])
            
            total_late_hours = sum(a.get('late_hours', 0) for a in employee_attendance if a['status'] == 'late')
            hourly_rate = employee['daily_salary'] / 8
            late_discount = total_late_hours * hourly_rate
            
            employee_advances = [a for a in advances_records if a['employee_id'] == employee['id']]
            total_advances = sum(a['amount'] for a in employee_advances)
            
            gross_salary = days_worked * employee['daily_salary']
            total_salary = gross_salary - late_discount
            net_payment = total_salary - total_advances
            
            trade = employee.get('trade', 'Sin rubro')
            if trade not in trade_totals:
                trade_totals[trade] = {
                    'employees': [],
                    'total': 0
                }
            
            trade_totals[trade]['employees'].append({
                'name': employee['name'],
                'days_worked': days_worked,
                'gross_salary': gross_salary,
                'late_discount': late_discount,
                'total_salary': total_salary,
                'advances': total_advances,
                'net_payment': net_payment
            })
            trade_totals[trade]['total'] += net_payment
            project_total += net_payment
        
        if project_employees:
            project_payments[project['id']] = {
                'project_id': project['id'],
                'project_name': project['name'],
                'trades': trade_totals,
                'total': project_total
            }
    
    unassigned_employees = [e for e in employees if not e.get('project_id')]
    if unassigned_employees:
        trade_totals = {}
        unassigned_total = 0
        
        for employee in unassigned_employees:
            employee_attendance = [a for a in attendance_records if a['employee_id'] == employee['id']]
            days_worked = sum(1 for a in employee_attendance if a['status'] in ['present', 'late'])
            
            total_late_hours = sum(a.get('late_hours', 0) for a in employee_attendance if a['status'] == 'late')
            hourly_rate = employee['daily_salary'] / 8
            late_discount = total_late_hours * hourly_rate
            
            employee_advances = [a for a in advances_records if a['employee_id'] == employee['id']]
            total_advances = sum(a['amount'] for a in employee_advances)
            
            gross_salary = days_worked * employee['daily_salary']
            total_salary = gross_salary - late_discount
            net_payment = total_salary - total_advances
            
            trade = employee.get('trade', 'Sin rubro')
            if trade not in trade_totals:
                trade_totals[trade] = {
                    'employees': [],
                    'total': 0
                }
            
            trade_totals[trade]['employees'].append({
                'name': employee['name'],
                'days_worked': days_worked,
                'gross_salary': gross_salary,
                'late_discount': late_discount,
                'total_salary': total_salary,
                'advances': total_advances,
                'net_payment': net_payment
            })
            trade_totals[trade]['total'] += net_payment
            unassigned_total += net_payment
        
        project_payments['unassigned'] = {
            'project_id': 'unassigned',
            'project_name': 'Sin asignar',
            'trades': trade_totals,
            'total': unassigned_total
        }
    
    return {"projects": list(project_payments.values())}


@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    today = datetime.now(timezone.utc)
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    
    all_employees = await db.employees.find({}, {"_id": 0}).to_list(1000)
    active_employees = [e for e in all_employees if e.get('is_active', True)]
    
    all_contractors = await db.contractors.find({}, {"_id": 0}).to_list(1000)
    active_contractors = [c for c in all_contractors if c.get('is_active', True)]
    
    attendance_records = await db.attendance.find({"week_start_date": week_start}, {"_id": 0}).to_list(5000)
    advances_records = await db.advances.find({"week_start_date": week_start}, {"_id": 0}).to_list(5000)
    
    total_payment = 0
    for employee in active_employees:
        employee_attendance = [a for a in attendance_records if a['employee_id'] == employee['id']]
        days_worked = sum(1 for a in employee_attendance if a['status'] in ['present', 'late'])
        
        # Calcular descuento por horas tarde
        total_late_hours = sum(a.get('late_hours', 0) for a in employee_attendance if a['status'] == 'late')
        hourly_rate = employee['daily_salary'] / 8
        late_discount = total_late_hours * hourly_rate
        
        total_payment += (days_worked * employee['daily_salary']) - late_discount
    
    contractors_payment = sum(c['weekly_payment'] for c in active_contractors)
    total_advances = sum(a['amount'] for a in advances_records)
    
    stats = DashboardStats(
        total_employees=len(all_employees),
        active_employees=len(active_employees),
        total_contractors=len(all_contractors),
        active_contractors=len(active_contractors),
        total_payment_this_week=total_payment,
        contractors_payment_this_week=contractors_payment,
        total_advances_this_week=total_advances,
        net_payment_this_week=total_payment - total_advances,
        total_to_pay_friday=total_payment + contractors_payment - total_advances
    )
    
    return stats


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
