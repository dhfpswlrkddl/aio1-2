"""
나만의 퀴즈 게임 (Console Quiz Game)
- 과제 요구사항: 객체 지향(최소 2개 클래스), 파일 영속성(state.json), 예외 처리, Git 버전 관리
"""

import json
import os
import sys


class Quiz:
    """개별 퀴즈를 표현하는 클래스"""

    def __init__(self, question: str, choices: list[str], answer: int):
        self.question = question
        self.choices = choices
        self.answer = answer  # 1~4 중 하나의 정답 번호

    def display(self, index: int = None) -> None:
        """문제를 화면에 포맷팅하여 출력"""
        prefix = f"[문제 {index}] " if index is not None else "[문제] "
        print(f"\n{prefix}{self.question}")
        for idx, choice in enumerate(self.choices, start=1):
            print(f"  {idx}. {choice}")

    def is_correct(self, user_answer: int) -> bool:
        """사용자가 입력한 답이 정답인지 확인"""
        return self.answer == user_answer

    def to_dict(self) -> dict:
        """JSON 저장을 위한 딕셔너리 변환"""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        """딕셔너리 데이터로부터 Quiz 객체 생성"""
        return cls(
            question=data.get("question", ""),
            choices=data.get("choices", []),
            answer=data.get("answer", 1),
        )


class QuizGame:
    """퀴즈 게임 전체를 관리하는 클래스"""

    def __init__(self, filepath: str = "state.json"):
        self.filepath = filepath
        self.quizzes: list[Quiz] = []
        self.best_score: int = 0
        self.load_data()

    def get_default_quizzes(self) -> list[Quiz]:
        """기본 퀴즈 6개 데이터 생성 (파이썬 상식, 일반 상식, 게임 상식)"""
        return [
            # 1. 파이썬 상식
            Quiz(
                question="[파이썬 상식] Python 프로그래밍 언어를 최초로 개발한 사람은 누구일까요?",
                choices=["리누스 토르발스", "귀도 반 로섬", "제임스 고슬링", "데니스 리치"],
                answer=2,
            ),
            Quiz(
                question="[파이썬 상식] Python에서 리스트의 맨 끝에 새로운 요소를 추가할 때 사용하는 메서드는?",
                choices=["add()", "push()", "append()", "insert()"],
                answer=3,
            ),
            # 2. 일반 상식
            Quiz(
                question="[일반 상식] 세계에서 가장 넓은 면적을 차지하는 바다(대양)는 어디일까요?",
                choices=["태평양", "대서양", "인도양", "북극해"],
                answer=1,
            ),
            Quiz(
                question="[일반 상식] 대한민국 헌법 제1조 제1항의 내용으로 올바른 것은?",
                choices=[
                    "대한민국은 민주공화국이다.",
                    "대한민국의 주권은 국민에게 있다.",
                    "모든 국민은 법 앞에 평등하다.",
                    "대한민국은 평화통일을 지향한다.",
                ],
                answer=1,
            ),
            # 3. 게임 상식
            Quiz(
                question="[게임 상식] 전 세계에서 누적 판매량 3억 장 이상으로 역대 가장 많이 팔린 게임은?",
                choices=["테트리스", "GTA V", "마인크래프트", "배틀그라운드"],
                answer=3,
            ),
            Quiz(
                question="[게임 상식] 닌텐도의 대표 캐릭터 '슈퍼 마리오'의 직업으로 가장 널리 알려진 것은?",
                choices=["소방관", "배관공", "경찰관", "탐정"],
                answer=2,
            ),
        ]

    def load_data(self) -> None:
        """state.json 파일에서 데이터를 불러오거나 예외 시 기본값으로 복구"""
        if not os.path.exists(self.filepath):
            print("📂 데이터 파일(state.json)이 없어 기본 퀴즈 데이터를 생성합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.save_data()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                raw_quizzes = data.get("quizzes", [])
                self.quizzes = [Quiz.from_dict(item) for item in raw_quizzes]
                self.best_score = data.get("best_score", 0)

            # 불러온 퀴즈 목록이 비어있는 경우 기본 퀴즈 복구
            if not self.quizzes:
                self.quizzes = self.get_default_quizzes()

            print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")

        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as e:
            print(f"⚠️ 데이터 파일이 손상되었거나 읽을 수 없습니다 ({e}). 기본 데이터로 복구합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.save_data()

    def save_data(self) -> None:
        """퀴즈 데이터와 최고 점수를 state.json에 UTF-8로 저장"""
        try:
            data = {
                "quizzes": [quiz.to_dict() for quiz in self.quizzes],
                "best_score": self.best_score,
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ 데이터 저장 중 오류가 발생했습니다: {e}")

    # ================= 공통 입력 검증 메서드 =================
    def prompt_int(self, prompt_text: str, min_val: int, max_val: int) -> int:
        """
        정수 입력 검증:
        - 앞뒤 공백 제거
        - 빈 입력(Enter) 처리
        - 정수 변환 실패(문자열 등) 예외 처리
        - 허용 범위(min_val ~ max_val) 검사
        """
        while True:
            raw_input = input(prompt_text).strip()
            if not raw_input:
                print("⚠️ 빈 입력입니다. 값을 입력해주세요.")
                continue

            try:
                val = int(raw_input)
            except ValueError:
                print(f"⚠️ 숫자가 아닙니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
                continue

            if val < min_val or val > max_val:
                print(f"⚠️ 허용 범위 밖입니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
                continue

            return val

    def prompt_text(self, prompt_text: str) -> str:
        """비어있지 않은 문자열 입력 검증"""
        while True:
            val = input(prompt_text).strip()
            if not val:
                print("⚠️ 필수 입력 항목입니다. 내용을 입력해주세요.")
                continue
            return val

    # ================= 메뉴별 기능 메서드 =================
    def display_menu(self) -> None:
        """메인 메뉴 출력"""
        print("\n" + "=" * 40)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        print("  1. 퀴즈 풀기")
        print("  2. 퀴즈 추가")
        print("  3. 퀴즈 목록")
        print("  4. 최고 점수 확인")
        print("  5. 퀴즈 삭제 (보너스 기능)")
        print("  0. 종료")
        print("=" * 40)

    def play_quiz(self) -> None:
        """퀴즈 출제 및 점수 계산, 최고점수 갱신"""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해주세요.")
            return

        print(f"\n📝 퀴즈를 시작합니다! (총 {len(self.quizzes)}문제)")
        correct_count = 0

        for idx, quiz in enumerate(self.quizzes, start=1):
            print("-" * 40)
            quiz.display(idx)
            user_ans = self.prompt_int("정답 입력 (1-4): ", 1, 4)

            if quiz.is_correct(user_ans):
                print("✅ 정답입니다!")
                correct_count += 1
            else:
                print(f"❌ 오답입니다. (정답: {quiz.answer}번)")

        # 점수 계산 (100점 만점 기준 환산)
        total_questions = len(self.quizzes)
        score = int((correct_count / total_questions) * 100)

        print("\n" + "=" * 40)
        print(f"🏆 결과: {total_questions}문제 중 {correct_count}문제 정답! ({score}점)")

        if score > self.best_score:
            print(f"🎉 축하합니다! 새로운 최고 점수입니다! (기존: {self.best_score}점 ➔ 신규: {score}점)")
            self.best_score = score
            self.save_data()
        else:
            print(f"현재 최고 기록: {self.best_score}점")
        print("=" * 40)

    def add_quiz(self) -> None:
        """새로운 퀴즈 등록"""
        print("\n" + "-" * 40)
        print("📌 새로운 퀴즈를 추가합니다.")
        print("-" * 40)

        question = self.prompt_text("문제를 입력하세요: ")
        choices = []
        for i in range(1, 5):
            choice = self.prompt_text(f"선택지 {i}: ")
            choices.append(choice)

        answer = self.prompt_int("정답 번호 (1-4): ", 1, 4)

        new_quiz = Quiz(question=question, choices=choices, answer=answer)
        self.quizzes.append(new_quiz)
        self.save_data()
        print("\n✅ 새로운 퀴즈가 성공적으로 추가 및 저장되었습니다!")

    def list_quizzes(self) -> None:
        """등록된 퀴즈 목록 조회"""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"[{idx}] {quiz.question}")
            for c_idx, choice in enumerate(quiz.choices, start=1):
                ans_mark = " (정답)" if c_idx == quiz.answer else ""
                print(f"    {c_idx}. {choice}{ans_mark}")
            print()
        print("-" * 40)

    def show_best_score(self) -> None:
        """최고 점수 확인"""
        print("\n" + "-" * 40)
        if self.best_score == 0:
            print("📊 아직 퀴즈를 완료한 기록이 없거나 최고 점수가 0점입니다.")
        else:
            print(f"🏆 현재 최고 점수: {self.best_score}점")
        print("-" * 40)

    def delete_quiz(self) -> None:
        """퀴즈 삭제 (보너스 기능)"""
        if not self.quizzes:
            print("\n⚠️ 삭제할 퀴즈가 없습니다.")
            return

        print(f"\n🗑️ 삭제할 퀴즈 번호를 선택하세요 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"[{idx}] {quiz.question}")
        print("[0] 삭제 취소")
        print("-" * 40)

        target_idx = self.prompt_int("선택 (0~삭제할 번호): ", 0, len(self.quizzes))
        if target_idx == 0:
            print("삭제를 취소했습니다.")
            return

        deleted_quiz = self.quizzes.pop(target_idx - 1)
        self.save_data()
        print(f"\n✅ [{target_idx}] '{deleted_quiz.question}' 퀴즈가 삭제되었습니다.")

    def run(self) -> None:
        """게임 실행 메인 루프 (예외 안전 처리)"""
        print("\n🎮 나만의 퀴즈 게임에 오신 것을 환영합니다!")
        while True:
            try:
                self.display_menu()
                choice = self.prompt_int("선택 (0-5): ", 0, 5)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_best_score()
                elif choice == 5:
                    self.delete_quiz()
                elif choice == 0:
                    print("\n게임을 종료합니다. 데이터를 안전하게 저장했습니다. 안녕히 가세요! 👋")
                    self.save_data()
                    break

            except (KeyboardInterrupt, EOFError):
                print("\n\n⚠️ 사용자에 의해 프로그램이 중단되었습니다.")
                print("데이터를 안전하게 저장하고 프로그램을 종료합니다. 👋")
                self.save_data()
                sys.exit(0)


if __name__ == "__main__":
    game = QuizGame(filepath="state.json")
    game.run()
