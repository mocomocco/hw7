#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import logging
import random
import webapp2
import sys

# Reads json description of the board and provides simple interface.
class Game:
	# Takes json or a board directly.
    def __init__(self, body=None, board=None):#bodyとboardの初期値はNone,もしbodyの中身があったならロード,もしなかったらboardの中身をロード
        if body:
            game = json.loads(body)
            self._board = game["board"]
        else:
            self._board = board

	# Returns piece on the board.
	# 0 for no pieces, 1 for player 1, 2 for player 2.
	# None for coordinate out of scope.
    def Pos(self, x, y):#（x、y）がボードの範囲内なら置いてある駒の種類を1か2で、範囲外ならNoneを返す
        return Pos(self._board["Pieces"], x, y)

	# Returns who plays next.
    def Next(self):#次のプレイヤーがどちらかを返す
        return self._board["Next"]

	# Returns the array of valid moves for next player.
	# Each move is a dict
	#   "Where": [x,y]
	#   "As": player number
    def ValidMoves(self):
		#次の人が置ける場所のリストを返す
        moves = []
        for y in xrange(1,9):
            for x in xrange(1,9):
                move = {"Where": [x,y],
                        "As": self.Next()}
                if self.NextBoardPosition(move):
                    moves.append(move)
        return moves

	# Helper function of NextBoardPosition.  It looks towards
	# (delta_x, delta_y) direction for one of our own pieces and
	# flips pieces in between if the move is valid. Returns True
	# if pieces are captured in this direction, False otherwise.
    def __UpdateBoardDirection(self, new_board, x, y, delta_x, delta_y):#x,yに置ける状態なら置いた後盤上データを更新し返り値はTrue。
        player = self.Next()
        opponent = 3 - player
        look_x = x + delta_x
        look_y = y + delta_y
        flip_list = []
        while Pos(new_board, look_x, look_y) == opponent:
            flip_list.append([look_x, look_y])
            look_x += delta_x
            look_y += delta_y
        if Pos(new_board, look_x, look_y) == player and len(flip_list) > 0:
                        # there's a continuous line of our opponents
                        # pieces between our own pieces at
                        # [look_x,look_y] and the newly placed one at
                        # [x,y], making it a legal move.
            SetPos(new_board, x, y, player)
            for flip_move in flip_list:
                flip_x = flip_move[0]
                flip_y = flip_move[1]
                SetPos(new_board, flip_x, flip_y, player)
            return True
        return False

# Takes a move dict and return the new Game state after that move.
# Returns None if the move itself is invalid.
    def NextBoardPosition(self, move):#moveの指定通りに置いて版を更新したgameを返す
        x = move["Where"][0]
        y = move["Where"][1]
        if self.Pos(x, y) != 0:# x,y is already occupied.
            return None
        new_board = copy.deepcopy(self._board)
        pieces = new_board["Pieces"]

        if not (self.__UpdateBoardDirection(pieces, x, y, 1, 0)
        		| self.__UpdateBoardDirection(pieces, x, y, 0, 1)
				| self.__UpdateBoardDirection(pieces, x, y, -1, 0)
				| self.__UpdateBoardDirection(pieces, x, y, 0, -1)
				| self.__UpdateBoardDirection(pieces, x, y, 1, 1)
				| self.__UpdateBoardDirection(pieces, x, y, -1, 1)
				| self.__UpdateBoardDirection(pieces, x, y, 1, -1)
				| self.__UpdateBoardDirection(pieces, x, y, -1, -1)):
                        # Nothing was captured. Move is invalid.
        	return None

                # Something was captured. Move is valid.
        new_board["Next"] = 3 - self.Next()
        return Game(board=new_board)

# Returns piece on the board.
# 0 for no pieces, 1 for player 1, 2 for player 2.
# None for coordinate out of scope.
#
# Pos and SetPos takes care of converting coordinate from 1-indexed to
# 0-indexed that is actually used in the underlying arrays.
def Pos(board, x, y):	#x,yがboard上ならそこに置いてある駒の種類を返す
	if 1 <= x and x <= 8 and 1 <= y and y <= 8:
		return board[y-1][x-1]
	return None

# Set piece on the board at (x,y) coordinate
def SetPos(board, x, y, piece):#x,yと駒の種類が正常ならboard更新
	if x < 1 or 8 < x or y < 1 or 8 < y or piece not in [0,1,2]:
		return False
	board[y-1][x-1] = piece

# Debug function to pretty print the array representation of board.
def PrettyPrint(board, nl="<br>"):#行列の中身を表示
	s = ""
	for row in board:
		for piece in row:
			s += str(piece)
		s += nl
	return s

def PrettyMove(move):#move["Where"]を表示
	m = move["Where"]
	return '%s%d' % (chr(ord('A') + m[0] - 1), m[1])

def countpiece(g,target):    #target=1 black target=2 white
    counter=0
    pieces=g._board["Pieces"]
    for piece in pieces:
        for p in piece:
            if target==1:
                if p==1:
                    counter+=1
            elif target==2:
                if p==2:
                    counter+=1
    return counter



class MainHandler(webapp2.RequestHandler):
    # Handling GET request, just for debugging purposes.
    # If you open this handler directly, it will show you the
    # HTML form here and let you copy-paste some game's JSON
    # here for testing.
    def get(self):#jsonをまだ読み込んでなければ入力画面、読み込んでいればpickMoveスタート
        if not self.request.get('json'):
            self.response.write("""
			<body><form method=get>
			Paste JSON here:<p/><textarea name=json cols=80 rows=24></textarea>
			<p/><input type=submit>
			</form>
			</body>
			""")
            return
        else:
            g = Game(self.request.get('json'))
            self.pickMove(g)

    def post(self):
    	# Reads JSON representation of the board and store as the object.
        g = Game(self.request.body)
        # Do the picking of a move and print the result.
        self.pickMove(g)

    def startstrategy(board,depth,valid_moves,playernum):#プレイヤー1側の視点
        if depth <1 :
            return countpiece(board,2)-countpiece(board,1)
        for move in valid_moves:
            nextboards=board.NextBoardPosition(move)

    def evaluate(self,g,validnum):
        numofblack=countpiece(g,1)
        numofwhite=countpiece(g,2)
        numall=numofblack+numofwhite
        if numofblack==0:
            return 0
        elif numall<12:
                return numofwhite
        elif numall<48:
            return validnum
        else:
            return numofblack


    def score(self,move,counter,g):
        valid_moves=g.ValidMoves()
        #for i in g._board["Pieces"]:
			#self.response.out.write("%d %d %d %d %d %d %d %d\n" %(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7]))
        #self.response.out.write("[%d %d]" %(move["Where"][0],move["Where"][1]))
        if g.NextBoardPosition(move):
            nextg=g.NextBoardPosition(move)
            #self.response.out.write("nextg\n")
            #for i in nextg._board["Pieces"]:
				#self.response.out.write("%d %d %d %d %d %d %d %d\n" %(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7]))
            #self.response.out.write("nextgfin\n")
            next_valid_moves=nextg.ValidMoves()
            nextlength=len(next_valid_moves)
            if nextlength==0:#パスあるいは終了
                if countpiece(nextg,1)+countpiece(nextg,2)==64:
                    return self.evaluate(nextg,nextlength)
                else:
                    return 10
            counter=counter-nextlength
            nextplayer=next_valid_moves[0]["As"]
            if counter<0:
                return self.evaluate(g,nextlength)
            else:
                if nextplayer==1:
                    best=-1
                elif nextplayer==2:
                    best=101
            for nextmove in next_valid_moves:
                new_score=self.score(nextmove,counter,nextg)
                if nextplayer==1:
                    if new_score>best:
                        best=new_score
                if nextplayer==2:
                    if new_score<best:
                        best=new_score
            return new_score
        else:
            return 10000

    def choosebestmove(self,valid_moves,g):
        counter=20
        player=valid_moves[0]["As"]
        if player==1:
            best=-1
        if player==2:
            best=101
        for move in valid_moves:
            new_score=self.score(move,counter,g)
            if player==1:
                if new_score>best:
                    best=new_score
                    best_move=move
            elif player==2:
                if new_score<best:
                    best=new_score
                    best_move=move
            #self.response.out.write("[%d %d]new_score:%d\n" %(move["Where"][0],move["Where"][1],new_score))
        return best_move

    def pickMove(self, g):# Gets all valid moves.
        numofblack=countpiece(g,1)
        numofwhite=countpiece(g,2)
        numall=numofblack+numofwhite
        valid_moves = g.ValidMoves()
        #///////////テスト用////////////
        #self.response.out.write("black:%d white:%d sum:%d\n" %(numofblack ,numofwhite ,numall))
        #///////////テスト用////////////
        if len(valid_moves) == 0:
            # Passes if no valid moves.
            self.response.write("PASS")
        else:
            # Chooses a valid move randomly if available.
                # TO STEP STUDENTS:
                # You'll probably want to change how this works, to do something
                # more clever than just picking a random move.
            move=self.choosebestmove(valid_moves,g)
            #move=minmax(depth,valid_moves)
            self.response.write(PrettyMove(move))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
