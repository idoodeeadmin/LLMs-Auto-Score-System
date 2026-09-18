from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List, Dict, Any, Literal

class UserRegister(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: Optional[str] = Field(default=None, max_length=255)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = 'unassigned'
    student_id: Optional[str] = None
    avatar_url: Optional[str] = None

    @model_validator(mode='after')
    def compute_full_name(self):
        if not self.name:
            fn = (self.first_name or '').strip()
            ln = (self.last_name or '').strip()
            self.name = f"{fn} {ln}".strip() or self.email
        return self

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    section: Optional[str] = Field(default=None, max_length=100)

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
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=10000)
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, max_length=10)

class SetRoleRequest(BaseModel):
    role: str
    identity_id: Optional[str] = None

class FirebaseLoginRequest(BaseModel):
    firebase_token: str

class QuestionInput(BaseModel):
    text: str
    score: float = Field(default=0, ge=0, allow_inf_nan=False)
    answer_key: Optional[str] = None
    rubrics: Optional[list] = None
    order_index: int = 0
    question_images_base64: Optional[List[str]] = Field(default=None, max_length=10)

class ExamCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    total_score: float = Field(default=0, ge=0, allow_inf_nan=False)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_randomized: int = 0
    questions: list[QuestionInput] = Field(min_length=1, max_length=100)
    draft_id: Optional[int] = None

    @model_validator(mode='after')
    def valid_exam_dates(self):
        from server.exam_policy import parse_exam_time
        start, end = parse_exam_time(self.start_date), parse_exam_time(self.end_date)
        if start and end and end <= start:
            raise ValueError('เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มสอบ')
        return self


class TimeExtensionRequest(BaseModel):
    student_id: Optional[int] = None
    extra_minutes: int
    note: Optional[str] = None

class GenerateRubricRequest(BaseModel):
    question_text: str
    total_score: float = Field(gt=0, allow_inf_nan=False)
    question_images_base64: Optional[List[str]] = Field(default=None, max_length=10)
    tone: Literal['simple', 'moderate', 'academic'] = 'moderate'

class QuestionBankCreate(BaseModel):
    text: str
    score: float = Field(default=0, ge=0, allow_inf_nan=False)
    answer_key: Optional[str] = None
    rubrics: Optional[list] = None
    tags: Optional[str] = None

class ExamDraftSave(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_randomized: int = Field(default=0, ge=0, le=1)
    questions: list[QuestionInput] = Field(min_length=1, max_length=100)

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

