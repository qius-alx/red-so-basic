from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash, current_app
)
from utils.decorators import login_required
from models.forum import Question, Answer
from models.activity_log import ActivityLog # Para registrar actividad
from math import ceil # Para la paginación

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')

@forum_bp.route('/', methods=['GET'])
@forum_bp.route('/questions', methods=['GET'])
@login_required # Generalmente, ver el foro requiere estar logueado.
def list_questions():
    """Muestra una lista paginada de preguntas del foro."""
    page = request.args.get('page', 1, type=int)
    per_page = 10 # O tomar de la configuración de la app: current_app.config.get('POSTS_PER_PAGE', 10)

    try:
        questions, total_questions = Question.get_all(page=page, per_page=per_page)
    except Exception as e:
        current_app.logger.error(f"Error al obtener preguntas del foro: {e}")
        flash("Error al cargar las preguntas del foro.", "danger")
        questions = []
        total_questions = 0

    total_pages = ceil(total_questions / per_page)

    return render_template(
        'forum/questions.html',
        questions=questions,
        current_page=page,
        total_pages=total_pages
    )

@forum_bp.route('/question/<int:question_id>', methods=['GET'])
@login_required
def view_question(question_id):
    """Muestra una pregunta específica y sus respuestas."""
    try:
        question = Question.find_by_id(question_id)
        if not question:
            flash("La pregunta no fue encontrada.", "warning")
            return redirect(url_for('forum.list_questions'))

        answers = Question.get_answers(question_id)

    except Exception as e:
        current_app.logger.error(f"Error al obtener la pregunta {question_id}: {e}")
        flash("Error al cargar la pregunta.", "danger")
        return redirect(url_for('forum.list_questions'))

    return render_template(
        'forum/view_question.html',
        question=question,
        answers=answers
    )

@forum_bp.route('/ask', methods=['GET', 'POST'])
@login_required
def ask_question():
    """Muestra el formulario para crear una nueva pregunta (GET) o la procesa (POST)."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        user_id = session.get('user_id')

        if not title or not content:
            flash('El título y el contenido son obligatorios.', 'danger')
            # Vuelve a mostrar el formulario con los datos que el usuario ya había ingresado
            return render_template('forum/ask_question.html', title=title, content=content), 400 # Bad Request

        if not user_id: # Seguridad adicional, aunque @login_required debería cubrirlo
            flash('Debes estar logueado para preguntar.', 'danger')
            return redirect(url_for('auth.login'))

        try:
            question_id = Question.create(user_id, title, content)
            if question_id:
                ActivityLog.log_forum_activity(user_id=user_id, action_type='create_question',
                                               item_id=question_id, ip_address=request.remote_addr)
                current_app.logger.info(f"Pregunta (ID: {question_id}) creada por usuario {user_id} y loggeada.")
                flash('Tu pregunta ha sido publicada.', 'success')
                return redirect(url_for('forum.view_question', question_id=question_id))
            else:
                flash('Hubo un error al publicar tu pregunta.', 'danger')
        except Exception as e:
            current_app.logger.error(f"Error al crear pregunta por usuario {user_id}: {e}")
            flash('Error interno al publicar tu pregunta. Inténtalo de nuevo.', 'danger')

        # Si algo falla después de la validación inicial, pero antes del redirect exitoso
        return render_template('forum/ask_question.html', title=title, content=content)

    # Método GET: simplemente muestra el formulario
    return render_template('forum/ask_question.html')

@forum_bp.route('/question/<int:question_id>/answer', methods=['POST'])
@login_required
def post_answer(question_id):
    """Procesa el formulario para añadir una nueva respuesta a una pregunta."""
    content = request.form.get('content', '').strip()
    user_id = session.get('user_id')

    if not content:
        flash('El contenido de la respuesta no puede estar vacío.', 'danger')
        # Redirigir de vuelta a la pregunta, idealmente mostrando el error.
        # Podríamos pasar un parámetro en la URL o usar más flash messages.
        return redirect(url_for('forum.view_question', question_id=question_id))

    if not user_id: # Seguridad adicional
        flash('Debes estar logueado para responder.', 'danger')
        return redirect(url_for('auth.login'))

    # Verificar que la pregunta exista antes de intentar añadir una respuesta.
    question = Question.find_by_id(question_id)
    if not question:
        flash('La pregunta a la que intentas responder no existe.', 'warning')
        return redirect(url_for('forum.list_questions'))

    try:
        answer_id = Answer.create(question_id, user_id, content)
        if answer_id:
            ActivityLog.log_forum_activity(user_id=user_id, action_type='create_answer',
                                           item_id=answer_id, ip_address=request.remote_addr) # item_id es answer_id
            current_app.logger.info(f"Respuesta (ID: {answer_id}) creada por usuario {user_id} para pregunta {question_id} y loggeada.")
            flash('Tu respuesta ha sido publicada.', 'success')
        else:
            flash('Hubo un error al publicar tu respuesta.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Error al crear respuesta por usuario {user_id} para pregunta {question_id}: {e}")
        flash('Error interno al publicar tu respuesta. Inténtalo de nuevo.', 'danger')

    return redirect(url_for('forum.view_question', question_id=question_id))
