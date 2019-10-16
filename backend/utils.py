def validate_new_question(question):
  if (question['question'] == "" or question['answer'] == "" or
      question['difficulty'] == "" or question['category'] == ""
    ):
    return False
  else:
    return True


