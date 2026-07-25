from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import CurrentUser, ensure_tenant_access, require_role, require_school
from app.services.report_service import ReportService
from app.models.school import School
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/csv")
def export_csv(
    school_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_school),
):
    """
    Export marketing intelligence report as CSV.
    School admins and marketing managers can export their own school data.
    Super admins can specify which school to export.
    """
    from uuid import UUID

    # Determine which school to export
    if school_id:
        if user.role_name != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only super admins can specify a school")
        try:
            school_id = UUID(school_id)
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid school ID")
    else:
        school_id = user.school_id

    # Verify school exists
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="School not found")

    # Verify tenant access if not super admin
    if user.role_name != "super_admin":
        ensure_tenant_access(school, user)

    service = ReportService(db)
    csv_content = service.generate_csv(school_id, start_date, end_date)

    if not csv_content:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate report")

    filename = f"report_{school.name.replace(' ', '_')}_{date.today()}.csv"
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/excel")
def export_excel(
    school_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_school),
):
    """
    Export marketing intelligence report as Excel (.xlsx).
    School admins and marketing managers can export their own school data.
    Super admins can specify which school to export.
    """
    from uuid import UUID

    # Determine which school to export
    if school_id:
        if user.role_name != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only super admins can specify a school")
        try:
            school_id = UUID(school_id)
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid school ID")
    else:
        school_id = user.school_id

    # Verify school exists
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="School not found")

    # Verify tenant access if not super admin
    if user.role_name != "super_admin":
        ensure_tenant_access(school, user)

    service = ReportService(db)
    excel_bytes = service.generate_excel(school_id, start_date, end_date)

    if not excel_bytes:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate report")

    filename = f"report_{school.name.replace(' ', '_')}_{date.today()}.xlsx"
    return StreamingResponse(
        iter([excel_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/pdf")
def export_pdf(
    school_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_school),
):
    """
    Export marketing intelligence report as PDF.
    School admins and marketing managers can export their own school data.
    Super admins can specify which school to export.
    """
    from uuid import UUID

    # Determine which school to export
    if school_id:
        if user.role_name != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only super admins can specify a school")
        try:
            school_id = UUID(school_id)
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid school ID")
    else:
        school_id = user.school_id

    # Verify school exists
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="School not found")

    # Verify tenant access if not super admin
    if user.role_name != "super_admin":
        ensure_tenant_access(school, user)

    service = ReportService(db)
    pdf_bytes = service.generate_pdf(school_id, start_date, end_date)

    if not pdf_bytes:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate report")

    filename = f"report_{school.name.replace(' ', '_')}_{date.today()}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
