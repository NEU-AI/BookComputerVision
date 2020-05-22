#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ai_camera import Camera
from ai_robot import Robot
from alphazero.human_play import Human
from alphazero.gameten import Board, Game
import cv2
from logger import logger_init
from alphazero.mcts_pure import MCTSPlayer as MCTS_Pure
from alphazero.mcts_alphaZero import MCTSPlayer
#from alphazero.policy_value_net_numpy import PolicyValueNetNumpy
#from alphazero.policy_value_net_tensorflow import PolicyValueNet
# from alphazero.policy_value_net import PolicyValueNet  # Theano and Lasagne
# from alphazero.policy_value_net_pytorch import PolicyValueNet  # Pytorch
##from alphazero.policy_value_net_tensorflow import PolicyValueNet # Tensorflow
from alphazero.policy_value_net_keras import PolicyValueNet  # Keras

class Controller(object):
    def __init__(self):
        self.game_state = 1  # 1 表示游戏没有结束，0表示结束
        self.logger = logger_init()
        self.camera = Camera(self.logger)
        self.robot = Robot()
        self.board = None

    # 机器人执行操作
    def action(self, move):
        # 从alphazero获取机器人的棋子索引值
        # 再次通知机械臂执行放子操作
        # 放子结束后机械臂结束放子后方法返回，需要增加一个等待时间再返回。
        location = self.board.move_to_location(move)
        self.robot.move(location)
        print ("robot:",location)

    # 等待人类操作：
    def wait_human(self):
        # 开启摄像头识别人类是否放了黑子,并获取人类房子的棋子索引值
        newchess = []
        count = 3
        prechess = []

        while 1:
            isfind,newchess = self.camera.findchess()
            #cv2.waitKey(1000)
            #print (1)
            if isfind:
                if prechess and prechess == newchess:
                    if count != 0:
                        count -= 1
                        print (2)
                        continue
                    else:
                        print (0)
                        self.camera.appendnewitem(prechess)
                        break
                elif prechess and prechess != newchess:
                    prechess = newchess
                    count = 3
                    print (3)
                elif len(prechess) == 0:
                    prechess = newchess
                    print (4)
                    continue

            if newchess is None:
                print ("keyboard End.")
                break
        return newchess

    # 判断是够游戏结束
    def is_end(self):
        if self.game_state == 0:
            return False
        else:
            return True

    def run(self):
        n = 5
        width, height = 8, 8
        model_file = './alphazero/best_policy_8_8_keras.model'
        try:
            board = Board(width=width, height=height, n_in_row=n)
            game = Game(board,self)

            # ############### human VS AI ###################
            # load the trained policy_value_net in either Theano/Lasagne, PyTorch or TensorFlow

            best_policy = PolicyValueNet(width, height, model_file=model_file)
            mcts_player = MCTSPlayer(best_policy.policy_value_fn, self,c_puct=5, n_playout=400)

            # human player, input your move in the format: 2,3
            human = Human(self)
            self.board = board
            # set start_player=0 for human first
            player = game.start_play(human, mcts_player, start_player=1, is_shown=0)
            if player is None:
                print ("force end.")
                return
            print(player.__str__())
        except KeyboardInterrupt:
            print('\n\rquit')

if __name__ == '__main__':
    controller = Controller()
    # 启动机械臂
    # controller.action(None)
    # newchess = controller.wait_human()
    #
    # while 1:
    #     controller.action(newchess)
    #     if controller.game_state == 0:
    #         break
    #     newchess = controller.wait_human()
    #     if cv2.waitKey(1) == ord('q'):
    #         break
    controller.run()

    cv2.destroyAllWindows()
