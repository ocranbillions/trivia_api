import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

from utils import *

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins.
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
      response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
      return response

  '''
  Gets all available categories
  '''
  @app.route('/categories')
  def get_categories():
    try:
        categories = Category.query.all()
        return jsonify({
            'categories': [category.format() for category in categories],
        }), 200
    except:
        abort(500)
        
  '''
  Get all questions 
  '''
  @app.route('/questions')
  def get_questions():
        page = request.args.get('page', 1, int)
        start = (page - 1) * 10
        end = start + 10
        try:
            questions = Question.query.order_by(Question.id).all()
            questions = [question.format() for question in questions]
            count = len(questions)
            categories = Category.query.order_by(Category.id).all()
            return jsonify({
                'questions': questions[start:end],
                'total_questions': count,
                'categories': [c.format() for c in categories],
            }), 200
        except:
            abort(500)


  '''
  Deletes a question from the database
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
      try:
          id = question_id
          question = Question.query.get(id)
          question.delete()
          return jsonify({
            'success': True,
            'message': "Successfully deleted"
          }), 200
      except:
          abort(422)


  '''
  Create new trivia questions 
  '''
  @app.route('/questions/create', methods=['POST'])
  def add_question():
    data = request.get_json()
    question = data.get('question', '')
    answer = data.get('answer', '')
    difficulty = data.get('difficulty', '')
    category = data.get('category', '')

    q = {}
    q['question'] = question
    q['answer'] = answer
    q['difficulty'] = difficulty
    q['category'] = category

    if validate_new_question(q) == False:
        abort(400)

    try:
        question = Question(
            question=question,
            answer=answer,
            difficulty=difficulty,
            category=category,
        )
        question.insert()
        return jsonify({
            'success': True,
            'message': 'Successfully Created!'
        }), 201
    except:
        abort(422)

  '''
  Search available questions  
  '''
  @app.route('/questions', methods=['POST'])
  def search_questions():
    body = request.get_json()
    term = body.get('searchTerm', '')

    if term == '':
        abort(400)
    try:  
        questions = Question.query.filter(Question.question.ilike(f'%{term}%')).all()
        count = len(questions)
        if count == 0:
            abort(404)
        questions = [q.format() for q in questions]  
        return jsonify({
        'success': True,
        'questions': questions
        }), 200
    except:
        abort(404)
  
  
  '''
  Get questions by their category 
  '''
  @app.route('/categories/<int:category_id>/questions') 
  def get_by_category(category_id):
    try:
        questions = Question.query.filter_by(category = category_id).all()
        questions = [q.format() for q in questions]
        count = len(questions)
        return jsonify({
            'questions': questions,
            'totalQuestions': count,
            'currentCategory': category_id
        })
    except:
        abort(500)

  '''
  Enable Game Play
  '''
  @app.route('/quizzes', methods=['POST'])
  def play():
    try:
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        category = data.get('quiz_category')
        
        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        random_index = random.randint(0, len(questions)-1)
        next_potential_question = questions[random_index]

        selected = False
        count = 0
        while selected is False:
            if next_potential_question.id in previous_questions:
                random_index = random.randint(0, len(questions)-1)
                next_potential_question = questions[random_index]
            else:
                selected = True
            if count == len(questions):
                break
            count += 1
        
        question = next_potential_question.format()
        return jsonify({
            'success': True,
            'question': question,
        }), 200
    except:
        abort(500)



  '''
  Create error handlers for all expected errors
  '''
  # handle bad request
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "message": "Bad Request, pls check your inputs"
    }), 400

  # handle resource not found errors
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "message": "Resource not found"
    }), 404

  # handle unprocessable entity errors
  @app.errorhandler(422)
  def unprocessable_entity(error):
      return jsonify({
          "success": False,
          "message": "Unprocessable Entity"
      }), 422

  # handle internal server errors
  @app.errorhandler(500)
  def internal_error(error):
      return jsonify({
          "success": False,
          "message": "Unable to load questions. Please try your request again"
      }), 500

  return app

    