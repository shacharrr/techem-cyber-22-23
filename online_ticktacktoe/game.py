import imgui

class TickTackToe():
    def __init__(self, game_code, is_game_owner) -> None:
        self.game_code = game_code
        self.game_chat = []
        self.board = [" "]*9

        self.is_startable = False
        self.is_over = True
        self.is_tie = True
        self.won = ""
        self.is_game_owner = is_game_owner
        self.sign = "X" if self.is_game_owner else "O"
        self.is_turn = self.sign == "X"

    def win_check(self):
        win = self.board[0] == self.board[1] == self.board[2] == self.sign or \
            self.board[3] == self.board[4] == self.board[5] == self.sign or \
            self.board[6] == self.board[7] == self.board[8] == self.sign or \
            self.board[0] == self.board[3] == self.board[6] == self.sign or \
            self.board[1] == self.board[4] == self.board[7] == self.sign or \
            self.board[2] == self.board[5] == self.board[8] == self.sign or \
            self.board[0] == self.board[4] == self.board[8] == self.sign or \
            self.board[2] == self.board[4] == self.board[6] == self.sign
        
        self.is_tie = True
        for b in self.board:
            if b == " ":
                self.is_tie = False

        self.is_over = win or self.is_tie
    
    def draw(self, name, width, height):
        n = None

        for i in range(len(self.board)):
            if imgui.button(f"[{self.board[i]}]##{i}", width//3, height//3-30):
                n = i
            if (i+1)%3 != 0 or i == 0:
                imgui.same_line()
        
        if n != None and self.board[n] == " " and not self.is_over and self.is_turn:
            self.board[n] = self.sign
            self.win_check()
            if self.is_over:
                self.won = name if not self.is_tie else "Tie"
            return 1
        
    def reset(self, name):
        self.board = [" "]*9
        if self.won == "Tie" or self.won == "":
            self.sign = "X" if self.is_game_owner else "O"
        else:
            self.sign = "X" if self.won == name else "O"
        self.is_turn = self.sign == "X"
        self.is_tie = True