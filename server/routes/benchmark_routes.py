from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import io

from server.services import benchmark_service

router = APIRouter(prefix="/api/benchmark", tags=["Benchmark & Model Evaluation"])

class EvaluateRequestItem(BaseModel):
    human_score: int
    ai_score: int
    question_no: Optional[int] = None
    answer_type: Optional[str] = "text"

class CustomEvaluationRequest(BaseModel):
    items: List[EvaluateRequestItem]

@router.get("/summary")
async def get_benchmark_summary():
    """
    Get overall benchmark summary metrics including:
    - Overall QWK, MAE, Agreement Level (Landis & Koch)
    - Confusion Matrix (6x6)
    - Modality breakdown (Text vs Handwriting Image)
    - Per-question performance (Q1-Q10)
    """
    try:
        metrics = benchmark_service.compute_benchmark_metrics()
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการคำนวณดัชนีชี้วัด: {str(e)}")

@router.get("/dataset")
async def get_benchmark_dataset(
    question_no: Optional[int] = Query(None, description="กรองตามข้อ (1-10)"),
    answer_type: Optional[str] = Query(None, description="กรองตามประเภทคำตอบ (text / img)"),
    difference: Optional[str] = Query(None, description="กรองตามผลต่างคะแนน (exact, near, divergent)"),
    confidence: Optional[str] = Query(None, description="กรองตามความมั่นใจ (High, Medium, Low)"),
    search: Optional[str] = Query(None, description="ค้นหาข้อความคำตอบ หรือเหตุผล"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=300)
):
    """
    Retrieve paginated dataset items with optional filters
    """
    try:
        items = benchmark_service.ensure_dataset_initialized()

        filtered = items
        if question_no is not None:
            filtered = [it for it in filtered if it.get("question_no") == question_no]

        if answer_type and answer_type.lower() != "all":
            filtered = [it for it in filtered if it.get("answer_type") == answer_type.lower()]

        if difference and difference.lower() != "all":
            diff_mode = difference.lower()
            if diff_mode == "exact":
                filtered = [it for it in filtered if it.get("difference", 0) == 0]
            elif diff_mode == "near":
                filtered = [it for it in filtered if it.get("difference", 0) == 1]
            elif diff_mode == "divergent":
                filtered = [it for it in filtered if it.get("difference", 0) >= 2]

        if confidence and confidence.lower() != "all":
            filtered = [it for it in filtered if str(it.get("ai_confidence", "")).lower() == confidence.lower()]

        if search and search.strip():
            kw = search.strip().lower()
            filtered = [
                it for it in filtered
                if kw in str(it.get("student_answer", "")).lower()
                or kw in str(it.get("transcription", "")).lower()
                or kw in str(it.get("ai_feedback", "")).lower()
                or kw in str(it.get("sample_id", "")).lower()
                or kw in str(it.get("topic", "")).lower()
            ]

        total = len(filtered)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_items = filtered[start_idx:end_idx]

        return {
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            "items": paginated_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการดึงข้อมูล Dataset: {str(e)}")

@router.post("/evaluate")
async def evaluate_custom_data(req: CustomEvaluationRequest):
    """
    Evaluate custom list of human & AI score pairs
    """
    if not req.items:
        raise HTTPException(status_code=400, detail="กรุณาส่งรายการคะแนนที่ต้องการวัดผล")

    raw_items = [
        {
            "human_score": it.human_score,
            "ai_score": it.ai_score,
            "question_no": it.question_no or 1,
            "answer_type": it.answer_type or "text"
        }
        for it in req.items
    ]

    metrics = benchmark_service.compute_benchmark_metrics(raw_items)
    return {
        "success": True,
        "data": metrics
    }

@router.get("/export")
async def export_benchmark_report():
    """
    Download benchmark report as Excel (.xlsx) file
    """
    try:
        excel_stream = benchmark_service.export_benchmark_excel()
        return StreamingResponse(
            excel_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=LLM_AutoScore_Benchmark_Report.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการสร้างไฟล์ Excel: {str(e)}")

@router.post("/import")
async def import_benchmark_data(file: UploadFile = File(...)):
    """
    Upload and parse .xlsx benchmark dataset
    """
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="รองรับเฉพาะไฟล์ Excel นามสกุล .xlsx เท่านั้น")

    try:
        content = await file.read()
        metrics = benchmark_service.import_benchmark_excel(content)
        return {
            "success": True,
            "message": "นำเข้าและประมวลผลชุดข้อมูลทดสอบสำเร็จ",
            "data": metrics
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการประมวลผลไฟล์: {str(e)}")

@router.post("/reset")
async def reset_benchmark_dataset():
    """
    Reset dataset to original 300 canonical Data Structures benchmark samples
    """
    try:
        fresh_data = benchmark_service.generate_default_benchmark_dataset()
        benchmark_service.save_dataset(fresh_data)
        metrics = benchmark_service.compute_benchmark_metrics(fresh_data)
        return {
            "success": True,
            "message": "รีเซ็ตชุดข้อมูลเป็นค่าเริ่มต้น 300 ตัวอย่างเรียบร้อยแล้ว",
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการรีเซ็ตชุดข้อมูล: {str(e)}")
