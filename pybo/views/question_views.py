import os
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, g, flash, current_app
from werkzeug.utils import secure_filename

from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.models import Question, Answer, User
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')


@bp.route('/list/')
def _list():
    page = request.args.get('page', 1, type=int)
    kw = request.args.get('kw', '', type=str)
    question_list = Question.query.order_by(Question.create_date.desc())

    if kw:
        search = '%%{}%%'.format(kw)
        # 1. 서브쿼리 작성 (답변과 답변자 정보를 미리 모음)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()

        # 2. 메인 쿼리에 조인 및 필터 적용
        question_list = question_list.join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(
            Question.subject.ilike(search) |  # 질문 제목
            Question.content.ilike(search) |  # 질문 내용
            User.username.ilike(search) |  # 질문 작성자
            sub_query.c.content.ilike(search) |  # 답변 내용
            sub_query.c.username.ilike(search)  # 답변 작성자
        ).distinct()

    question_list = question_list.paginate(page=page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw)

@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html', question=question, form=form)

@bp.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        # 폼에 전송된 이미지 파일 가져오기
        image_file = form.image.data
        image_path = None

        if image_file:
            # 저장 경로 : 오늘 날짜로 폴더 설정
            today = datetime.now().strftime('%Y%m%d')
            upload_folder = os.path.join(current_app.root_path, 'static/photo', today)
            os.makedirs(upload_folder, exist_ok=True)

            # 파일 저장
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)

            # DB에 저장할 파일 경로(static 기준 상대경로)
            image_path = f'photo/{today}/{filename}'

        question = Question(
            subject=form.subject.data,
            content=form.content.data,
            create_date=datetime.now(),
            user=g.user,
            image_path=image_path
        )
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form)

@bp.route('/modify/<int:question_id>/', methods=['GET', 'POST'])
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정 권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date=datetime.now() # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question.id))
    else:
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)

@bp.route('/delete/<int:question_id>/')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))