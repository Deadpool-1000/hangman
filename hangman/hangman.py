import logging
from hangman.basegame import BaseGame
from hangman.graphic import hanged
from word_section.words import WordMachine
from word_section.words import OutOfWordsError
from config.hangman_config import HangmanConfig
from config.logs_config import LogsConfig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player.player import Player

logger = logging.getLogger("main.hangman")


class Hangman(BaseGame):
    """
    This class implements all the game functionalities
    Accepts only one argument of type <Player> during initialisation
    """
    def __init__(self, player: 'Player', num_of_rounds, difficulty=8):
        super().__init__(player)
        self.num_of_rounds: int = num_of_rounds
        self.left_chances: int = 7
        self.completed_rounds = 0
        self.guessed_letters: list[str] = []
        self.correctly_guessed: list[str] = []
        self.current_letter: str | None = None
        self.current_word: str | None = None
        self.current_description: str | None = None
        self.difficulty = difficulty
        self.word_machine = WordMachine()

    def get_random_word_and_description(self) -> tuple[str, str]:
        random_word: dict = self.word_machine.get_random_word(self.difficulty)
        word = random_word['word']
        description = random_word['hint']
        return word, description

    def reset_game(self) -> None:
        self.left_chances = 7
        self.guessed_letters.clear()
        self.correctly_guessed.clear()
        self.current_word = None
        self.current_letter = None
        self.current_description = None

    def start_game(self) -> None:
        print()
        print(HangmanConfig.WELCOME_TO_GAME.format(self.player.name))

        try:
            while self.completed_rounds < self.num_of_rounds:
                print()
                print(HangmanConfig.ROUND_INFO.format(self.completed_rounds+1))  # It will be total self.num_of_rounds - self.num_of_rounds(var) + 1
                self.current_word, self.current_description = self.get_random_word_and_description()
                score = self.play_game()  # Calls the playing routine for self.player
                self.update_scores(score)  # reflect scores on the players object
                self.results(score, self.completed_rounds)
                self.reset_game()  # reset hangman variables
                self.completed_rounds += 1
            self.declare_results()
            won_rounds = self.calculate_rounds_won()
            self.exit_game(self.completed_rounds, won_rounds)
        except OutOfWordsError as oe:
            print(oe)
            logger.error(LogsConfig.OUT_OF_WORDS_ERROR_LOG)

    def play_game(self) -> int:
        while self.left_chances != 0 and not self.all_guessed_correctly():
            self.generate_prompt(self.current_word, self.current_description)
            letter_guessed = Hangman.input_letter()
            while self.is_already_guessed(letter_guessed):
                print(HangmanConfig.ALREADY_GUESSED)
                letter_guessed = Hangman.input_letter()
            if not self.validate_input(letter_guessed):
                self.left_chances -= 1
                print(hanged(6-self.left_chances))
            else:
                print(HangmanConfig.CORRECT_GUESS)
        print("\n---------------------------------------------------")
        if self.all_guessed_correctly():
            print(HangmanConfig.ALL_GUESSED_CORRECTLY.format(self.current_word))
        elif self.left_chances == 0:
            print(HangmanConfig.NOT_GUESSED_CORRECTLY.format(self.current_word))
        return self.left_chances

    def all_guessed_correctly(self) -> bool:
        s1 = set(self.correctly_guessed)
        s2 = set(self.current_word)
        return True if len(s1) == len(s2) else False

    def is_already_guessed(self, letter_guessed) -> bool:
        return True if letter_guessed in self.guessed_letters else False

    def validate_input(self, letter_guessed) -> bool:
        self.guessed_letters.append(letter_guessed)
        if letter_guessed in self.current_word:
            self.correctly_guessed.append(letter_guessed)
            return True
        else:
            return False

    def generate_prompt(self, word, description) -> None:
        print(HangmanConfig.HANGMAN_WORD, end='\t')
        for ch in word:
            print(ch if ch in self.correctly_guessed else "_", end=' ')
        print(HangmanConfig.HANGMAN_CHANCES, self.left_chances, "/7")
        print(HangmanConfig.HANGMAN_HINT, description)

    @staticmethod
    def input_letter() -> str:
        user_input = input(HangmanConfig.YOUR_GUESS).strip()
        while len(user_input) != 1:
            user_input = input(HangmanConfig.ENTER_SINGLE_CHARACTER).strip()
        return user_input

    def update_scores(self, score) -> None:
        """
        Stores the score of the current round in players->score list
        :param score:
        :return: None
        """
        self.player.scores.append(score)

    def results(self, score: int, game_round: int) -> None:
        logger.debug(LogsConfig.PLAYER_RESULT_DEBUG.format(self.player.name, score))
        print(HangmanConfig.RESULT_OF_SINGLE_ROUND.format(score, game_round + 1))
        print("---------------------------------------------------")
