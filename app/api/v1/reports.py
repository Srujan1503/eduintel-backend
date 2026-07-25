from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import csv
import io

from app.database.session import get_db
from app.auth.dependencies import require_role

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/csv")
def reports_csv(db: Session = Depends(get_db), _ = Depends(require_role("super_admin"))):
    # Placeholder CSV with headers
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "note"])
    writer.writerow(["1", "sample", "placeholder"])
    return Response(content=output.getvalue(), media_type="text/csv")


@router.get("/excel")
def reports_excel(db: Session = Depends(get_db), _ = Depends(require_role("super_admin"))):
    # Returning CSV as placeholder for excel
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "note"])
    writer.writerow(["1", "sample", "placeholder"])
    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/pdf")
def reports_pdf(db: Session = Depends(get_db), _ = Depends(require_role("super_admin"))):
    # Placeholder PDF response
    return Response(content=b"%PDF-1.4\n%placeholder\n", media_type="application/pdf")
