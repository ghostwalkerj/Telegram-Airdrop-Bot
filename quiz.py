import random


class QuizAnswer():
    def __init__(self, answer: str, correct: bool):
        self.answer = answer
        self.correct = correct

    def __str__(self):
        qa = self.answer
        if (self.correct):
            qa += ": Correct Answer"
        return qa

    def __repr__(self):
        return self.__str__()


class QuizQuestion():
    question: str
    answers: list[QuizAnswer]

    def __init__(self, question: str):
        self.question = question
        self.answers = []

    def __str__(self):
        qs = "\n\nQuestion: " + self.question + \
            "\n\nAnswers: " + str(self.answers)
        # for aq in self.answers:
        #     qs += "\n\n"
        #     qs += str(aq)
        return qs

    def __repr__(self):
        return self.__str__()

    def add_answer(self, answer: QuizAnswer):
        self.answers.append(answer)

    def correct_answer(self) -> str:
        letter = 'a'
        for qa in self.answers:
            if qa.correct:
                return letter
            letter = chr(ord(letter)+1)
        return letter


class Quiz():
    @staticmethod
    def quiz_list_from_config(config: dict) -> list[QuizQuestion]:
        questions: list[QuizQuestion] = []
        for question in config:
            qq = QuizQuestion(question)
            all = None
            for answer in config[question]:
                if answer[0] == '*':
                    answer = answer[1:]
                    if answer.startswith('#ALL'):
                        all = QuizAnswer('All of the above', True)
                    else:
                        qa = QuizAnswer(answer, True)
                        qq.add_answer(qa)
                elif answer.startswith('#ALL'):
                    all = QuizAnswer('All of the above', False)
                else:
                    qa = QuizAnswer(answer, False)
                    qq.add_answer(qa)
            random.shuffle(qq.answers)
            if all:
                qq.add_answer(all)
            questions.append(qq)
            random.shuffle(questions)
        return questions

    # Prints question in a format for display
    @staticmethod
    def to_pretty_string(qq: QuizQuestion) -> str:
        pp = qq.question + "\n"
        letter = 'a'
        for qa in qq.answers:
            pp += "\t" + letter + ") " + qa.answer + "\n"
            letter = chr(ord(letter)+1)
        return pp
