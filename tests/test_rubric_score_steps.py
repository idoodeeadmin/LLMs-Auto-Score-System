from server.services.rubric_score_steps import allowed_total_scores


def test_combines_explicit_partial_credit_levels():
    rubrics = [
        {"score": 0.5, "description": "0.50 คะแนน: ถูกครบ; 0.25 คะแนน: ถูกบางส่วน; 0.00 คะแนน: ไม่ตอบ"},
        {"score": 0.5, "description": "0.50 คะแนน: ครบ; 0.25 คะแนน: บางส่วน; 0.00 คะแนน: ไม่มี"},
    ]
    assert allowed_total_scores(rubrics, 1) == [0, 0.25, 0.5, 0.75, 1]


def test_does_not_invent_steps_for_incomplete_rubric():
    rubrics = [{"score": 2, "description": "พิจารณาความถูกต้องของคำตอบ"}]
    assert allowed_total_scores(rubrics, 2) is None


def test_rejects_levels_outside_criterion_maximum():
    rubrics = [{"score": 1, "description": "2 คะแนน: ตัวอย่าง; 1 คะแนน: ถูก; 0 คะแนน: ผิด"}]
    assert allowed_total_scores(rubrics, 1) is None
