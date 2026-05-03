from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    role: Optional[str] = 'unassigned'
    student_id: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RoomCreate(BaseModel):
    name: str
    section: Optional[str] = None

class JoinRoomRequest(BaseModel):
    class_code: str

class ForgotPasswordRequest(BaseModel):
    email: str
    name: Optional[str] = None
    student_id: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: str

class AnnouncementCreate(BaseModel):
    title: str
    content: str

class SetRoleRequest(BaseModel):
    role: str
    student_id: Optional[str] = None

class FirebaseLoginRequest(BaseModel):
    firebase_token: str

class QuestionInput(BaseModel):
    text: str
    score: float = 0
    answer_key: Optional[str] = None
    rubrics: Optional[list] = None
    order_index: int = 0
    question_images_base64: Optional[List[str]] = None

class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    total_score: float = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_randomized: int = 0
    questions: list[QuestionInput] = []

class TimeExtensionRequest(BaseModel):
    student_id: Optional[int] = None
    extra_minutes: int
    note: Optional[str] = None

class GenerateRubricRequest(BaseModel):
    question_text: str
    total_score: float
    question_images_base64: Optional[List[str]] = None
    tone: Optional[str] = 'moderate'

class QuestionBankCreate(BaseModel):
    text: str
    score: float = 0
    answer_key: Optional[str] = None
    rubrics: Optional[list] = None
    tags: Optional[str] = None

class DraftSaveRequest(BaseModel):
    answers: dict

class SubmitAnswerInput(BaseModel):
    question_id: int
    answer_text: str

class SubmitExamRequest(BaseModel):
    answers: List[SubmitAnswerInput]

class ApproveSubmissionRequest(BaseModel):
    teacher_scores: Optional[dict] = None
    teacher_comments: Optional[dict] = None

class BulkApproveRequest(BaseModel):
    student_ids: List[int]

