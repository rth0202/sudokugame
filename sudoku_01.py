import sys
import pygame
import numpy as np
import random
import time
import operator
import copy


from pygame.color import THECOLORS as cols

from build import print_matrix,give_me_a_game,check

# Author: 

defaultGridSize = 42 # grid size (default)
DEBUG = 1
SHOWPROCESS = 1
REFRESH = 1



def getSudokuByLib(seed = time.time(), selectNum = -1, isPrint = DEBUG):

    sudokuStrLib = ["000001000 200907000 900405801 500070080 000500704 040080006 003050020 100000040 000600307",  # 1
    "090006005 047001690 601590000 005000002 070000080 300200740 002430000 009000108 000000000", 
    "000500204 000700006 172300009 356007000 000000000 000400317 700008925 200001000 609004000", 
    "230008070 005006002 600000005 007009000 390105800 061000000 809501600 006004090 000000200", 
    "005300000 800000020 070010500 400005300 010070006 003200080 060500009 004000030 000009700",  # 5
    "000000000 040030802 063009050 000001904 800000001 304700000 020300670 105020080 000000000", 
    "520970000 000000000 009800040 407008090 010090030 030600801 080005300 000000000 000082067", 
    "610530000 000000000 002700080 903006010 040020090 070400508 020004700 000000000 000019052", 
    "470390000 000000000 009200070 508006020 090070080 060800401 050004300 000000000 000058067", 
    "480390000 000000000 006200030 605008020 010050090 040100307 020001900 000000000 000075086",  # 10
    "560740000 000000000 008100030 901002060 070010090 080600105 090006200 000000000 000023074", 
    "920530000 000000000 008400030 306002070 070060050 050100806 040007600 000000000 000091082", 
    "310240000 000000000 006800010 708004060 090080030 040500107 050001200 000000000 000092045", 
    "800000000 003600000 070090200 050007000 000045700 000100030 001000068 008500010 090000400", 
    "000800000 040000200 000010807 092034008 030000700 050002630 000201000 003005070 007640090",  # 15
    "007150003 160000000 354002900 000000059 405901607 970000000 009400178 000000092 700093500", 
    "800000000 003600000 070090200 050007000 000045700 000100030 001000068 008500010 090000400", 
    "000000039 000001005 003050800 008090006 070002000 100400000 009080050 020000600 400700000", 
    "009000300 030908070 700010009 020706040 008000700 090204060 300040005 010807030 006000400", 
    "100200300 040000000 000005060 200706500 000080000 006904010 800300200 007009004 000000090",  # 20
    "000120300 030000004 005000060 200403700 800000010 000902000 100800000 009070005 060000030", 
    "000820030 900001800 000403160 036700900 708000000 450002006 000074308 001000600 000060092", 
    "002000000 900018700 000036080 329000000 005097036 107800400 000500010 030000008 001300054"]

    num = len(sudokuStrLib)
    if selectNum >= 0 and selectNum < num: 
        if isPrint: print("GAME NUMBER: " + str(selectNum))
        return sudokuStrLib[selectNum], selectNum

    random.seed(seed)
    if selectNum == -2: 
        selectNum = num - 1
    else:
        selectNum = int(random.uniform(0, num))

    while selectNum in []: # blacklist
        selectNum = int(random.uniform(0, num))

    if isPrint: print("GAME NUMBER: " + str(selectNum))
    return sudokuStrLib[selectNum], selectNum

testSudokuStr, testNum = getSudokuByLib(selectNum = -1)
# 数独部分



def emptyList(l = 1): # 生成长度为l的空列表，每个列表的指针并不相同
    r = []
    for k in range(l):
        r.append(list())
    return r

def multiList(list0 = [], l = 1):
    r = []
    for k in range(l):
        r.append(copy.deepcopy(list0))
    return r

def mask(lst, m):
    # 例子：
    # mask([[1, 2, 3], [2, 4], [5], [3]], '0101') -> [[2, 4], [3]]
    m = m.zfill(len(lst))
    return map(lambda x: x[0],  filter(lambda x: x[1]!='0',  zip(lst, m)))

def allunion(lst):
    r = set()
    for k in lst:
        r = r.union(set(k))
    return r

class sudoku(object):
    def __init__(self, s = testSudokuStr):
        self.str = s # str类型的数独（初始）
        self.array0 = self.str2array(s) # array类型的数独（初始）
        self.arr = self.array0.copy() # array类型的数独（当前）
        self.calcarr = np.zeros((9, 9)) # 暂时没用，用于存储被程序自动计算的格子，如果被计算则记为2
        self.colarr = np.zeros((9, 9)) # 颜色矩阵
        self.trynum_help = emptyList(81) # 电脑计算出的试错列表，用于继承之前的结果
        self.trynum = emptyList(81) # 试错列表，就是尝试数，是显示出来的草稿
        self.help(init = True)

    def deepcopy(self): # NOT FINISHED
        obj = sudoku()
        obj.arr = self.arr.copy()
        obj.trynum = copy.deepcopy(self.trynum)


    def str2array(self, s):
        s = s.replace(" ", "")
        if len(s) != 81:
            raise Exception("Wrong length of sudoku: ", len(s))
        m = np.zeros((9, 9))
        for k in range(81):
            m[k // 9, k % 9] = int(s[k])
        return m

    def check(self, num9): # 检查9个数中是否有重复数字，有则返回重复的两个序号，没有返回两个0
        n = num9.flatten()
        for j in range(8):
            if n[j] == 0: 
                continue
            for k in range(j + 1, 9):
                if n[j] == n[k]: return j,k
        return 0,0

    def checkRow(self, r):  # 检查某一行是否有重复数字，有则返回重复的两个序号，没有返回两个0
        a = self.arr[r, :]
        return self.check(a)

    def checkCol(self, c):  # 列
        a = self.arr[:, c]
        return self.check(a)

    def getCurSquare(self, i, j): # 获得第i行第j列对应的九宫格数据
        z = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
        r = z[i // 3]
        c = z[j // 3]
        a = self.arr[r, :]
        a = a[:, c]
        return a

    def checkSquare(self, num):  # 九宫格
        x = num // 3
        y = num % 3
        z = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
        a = self.arr[z[x], :]
        a = a[:, z[y]]
        return self.check(a)

    def checkAll(self): # 检查所有格子中是否有错误，返回所有错误坐标（没有错误返回空列表）
        z = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
        wrongLocate = []
        for k in range(9):
            _temp = self.checkRow(k)
            if (_temp[1] != 0):
                wrongLocate.append((k, _temp[0]))
                wrongLocate.append((k, _temp[1]))
            _temp = self.checkCol(k)
            if (_temp[1] != 0):
                wrongLocate.append((_temp[0], k))
                wrongLocate.append((_temp[1], k))
            _temp = self.checkSquare(k)
            if (_temp[1] != 0):
                wrongLocate.append(((k // 3) * 3 + _temp[0] // 3, (k % 3) * 3 + _temp[0] % 3))
                wrongLocate.append(((k // 3) * 3 + _temp[1] // 3, (k % 3) * 3 + _temp[1] % 3))
        wrongLocate = set(wrongLocate)

        # 改变颜色矩阵
        self.colarr = np.zeros((9, 9))
        for j in wrongLocate: self.colarr[j] = 1
        self.colarr = self.colarr + self.calcarr
        if DEBUG: print("-| Check wrong locates: " + str(wrongLocate))
        return(wrongLocate)

    def checkWin(self): 
        if self.arr.all() and not len(self.checkAll()): 
            return 1
        return 0

    def _helpByNum(self, m0, num, type = 'r'):
        # num: range(9)
        j = num
        _temp = []
        _tempnum = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        count = 0
        # 检测某一行/列/九宫格能否填写数字
        if type == 'r':
            for k in range(9):
                _temp = _temp + m0[j * 9 + k]
                # 统计temp中每个元素的个数
            for k in range(9):
                _tempnum[k] = _temp.count(k + 1)
                if _tempnum[k] == 1: # 有某个数字k + 1仅有一个可能位置
                    for l in range(9):
                        if (k + 1) in m0[j * 9 + l]: 
                            if self.array0[j, l] != 0: raise Exception("Wrong position, level 1, (r" + str(num) + "):", j, l)
                            count = count + 1
                            self.arr[j, l] = k + 1
                            self.calcarr[j, l] = 2
                            if DEBUG: print("--| level 1, (r" + str(num) + ") (" + str(j) + ", " + str(l) + ") <- ", k + 1)
        elif type == 'c':
            for k in range(9):
                _temp = _temp + m0[k * 9 + j]
            for k in range(9):
                _tempnum[k] = _temp.count(k + 1)
                if _tempnum[k] == 1:
                    for l in range(9):
                        if (k + 1) in m0[l * 9 + j]: 
                            if self.array0[l, j] != 0: raise Exception("Wrong position, level 1, (c" + str(num) + "):", j, l)
                            count = count + 1
                            self.arr[l, j] = k + 1
                            self.calcarr[l, j] = 2
                            if DEBUG: print("--| level 1, (c" + str(num) + ") (" + str(l) + ", " + str(j) + ") <- ", k + 1)
        elif type == 's':
            for k in range(9):
                _temp = _temp + m0[((j // 3) * 3 + k // 3) * 9 + (j % 3) * 3 + k % 3]
            # 统计temp中每个元素的个数
            for k in range(9):
                _tempnum[k] = _temp.count(k + 1)
                if _tempnum[k] == 1:
                    for l in range(9):
                        xl, yl = ((j // 3) * 3 + l // 3), (j % 3) * 3 + l % 3
                        if (k + 1) in m0[xl * 9 + yl]: 
                            if self.array0[xl, yl] != 0: 
                                raise Exception("Wrong position, level 1, (n" + str(num) + "):", xl, yl)
                            count = count + 1
                            self.arr[xl, yl] = k + 1
                            self.calcarr[xl, yl] = 2
                            if DEBUG: print("--| level 1, (n" + str(num) + ") (" + str(xl) + ", " + str(yl) + ") <- ", k + 1)
        else:
            raise Exception("Wrong type in sudoku()._helpByNum: type " + str(type) + "is not in {'c', 'r', 's'}." )
        return count

    def _helpByType(self, m0, type = 'r'):
        count = 0
        for k in range(9):
            count = count + self._helpByNum(m0 = m0, num =  k, type = type)
        return count


    def _checkMulti_9Num(self, a, type = 'r', num = 0):
        # 思路：采用0-1的想法，选中的集合为1，未选中的集合为0
        # 比如，7个有效集合，0100010表示选中了1，5（首个为0）
        # a: 一个len = 9的列表，是需要改的列表！
        # type and num: only for debug

        rn = len(a) - a.count([])
        if rn <= 2: return
        a0 = []
        m = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # 获取实际序号
        for k in range(9):
            if a[k] == []: 
                m.remove(k + 1)
            else:
                a0.append(a[k])
        # 暴力遍历
        # 全是0或1的不需要
        # 只有1个1的或只有1个不是1的不需要
        # 只有1个不是1：假如成立，可以推出剩下的那个至多出现1次，那用lv 1的排除法即解决

        for k in range(2 ** rn):
            # 1. 得到形如'010010'的字符串
            s = bin(k)[2:]
            s = s.zfill(rn)
            # 1.1 如果选取元素数量不符合，跳过
            if s.count('1') in [0, 1, rn - 1, rn]: continue

            # 2. 获取子集
            _subset = copy.deepcopy(list(mask(a0, s)))

            # 3. 计算所有集合的交
            _subsetunion = allunion(_subset)

            # 4. 计算元素个数和s.count是否相同，相同则进行处理，否则下一个
            # 处理：把其它列表中的该元素删除
            rcount = len(_subsetunion)
            if rcount > s.count('1'): continue

            if DEBUG: 
                s0 = "("
                for _k in range(rn):
                    if s[_k] == '1' and s0 == "(":
                        s0 = s0 + str(m[_k]) 
                    elif s[_k] == '1':
                        s0 = s0 + ", " + str(m[_k])
                s0 = s0 + ")"
                print("--| lv.3, (" + type + str(num) + ") - " + s0 + ": " + str(_subsetunion))

            for k in range(rn):
                if(s[k] == '0'): 
                    # 其它集合
                    for j in _subsetunion:
                        if j in a0[k]: 
                            a0[k].remove(j) # 由于指向同一个指针，a对应的元素也被删除
                            if DEBUG: print("---| " + "(" + type + str(num) + ", " + str(k) + "): remove " + str(j))

        return

    def _checkMultiByNum(self, m0, num, type = 'r'):
        if type == 'r':
            _num = num * 9
            a = m0[_num:(_num + 9)]
            self._checkMulti_9Num(a, type = type, num = num)
        elif type == 'c':
            _num = num % 9
            a = []
            for k in range(9):
                a.append(m0[_num + 9 * k])
            self._checkMulti_9Num(a, type = type, num = num)
        elif type == 's':
            i0 = (num // 3) * 3
            j0 = (num % 3) * 3
            a = []
            for i in range(3):
                for j in range(3):
                    a.append(m0[(i + i0) * 9 + (j + j0)])
            self._checkMulti_9Num(a, type = type, num = num)
        return



    def _checkMultiNumByType(self, m0, type = 'r'):
        for k in range(9):
            self._checkMultiByNum(m0 = m0, num = k, type = type)
        return

    # def _checkXYWingByLine(self, num = 2):
        ## ----






    def help(self, s0 = 'START', level = 1, trytime = 81, init = False, tryOnly = False, iter = 0): 
        # help
        # level:
        # 1级：检测行，列，九宫格能否使用简单排除 (finish)
        # 2级：1级 + 检验某个格子是否有唯一可填数 (finish)
        # 3级：2级 + 检测是否有某n个格子的联合排除
        # 4级：3级 + 使用树形排除尝试某个格子。要求该格子仅有至多两个选项。

        # trytime: 累计迭代尝试次数。由于无法排除时程序终止，故trytime >= 81时实际上等价于完全排除。
        # a: 用于4级排除时的临时数独
        # init: True时仅用于初始创建self.trynum_help 对象
        # 同时可用于试错后重建列表

        # tryOnly: True时仅用于辅助排除，会把trynum与得到的排除结果取交集

        # Output:
        # 修改电脑帮助部分的数据
        # type = 1时将填写格子，2时仅辅助不填写
        if DEBUG: print("Help: level = " + str(level) + ", trytime = " + str(trytime))
        if DEBUG and init: print("Init: True")
        if DEBUG and tryOnly: print("tryOnly: True")

        if len(self.checkAll()) > 0:
            if DEBUG: print("sudoku().help() stop: Failed in sudoku().checkAll().")
            if level >= 4 and DEBUG: print("--| lv.4 Failed this way: " + s0 + " (iter = " + str(iter) + ")")
            return -1

        if SHOWPROCESS: self.trynum = copy.deepcopy(self.trynum_help)
        if not init and iter <= 1: 
            if REFRESH: refresh()

        a = self.arr # 使用当前的数独
        a_line = self.arr.flatten()

        if init: # 初始
            m0 = multiList([1, 2, 3, 4, 5, 6, 7, 8, 9], 81)
        else:
            m0 = self.trynum_help 

        for k in range(81):
            if a_line[k]: 
                m0[k] = []
        count = 0 # 计数，判断能计算多少格子

        if level >= 1:
            for k in range(81):
            # 使用简单排除，把不符合的部分从m0移除
            # 同一行：除9的整数部分相同；同一列：除9的余数相同
            # 同一个九宫格：行和列除以3的余数分别相同
                a1 = k // 9
                c1 = k % 9
                gr9 = self.getCurSquare(a1, c1)
                m0[k] = list(set(m0[k]).difference(set(a[a1, :])).difference(set(a[:, c1])).difference(set(gr9.flatten())))

        self.trynum_help = m0 # lv2处理后的替代
        # 如果出现用户试错时，这也可以用于重新更新列表
        
        if init and level == 1:
            return
        elif tryOnly and level <= 2: # 辅助时1级和2级没啥区别
            for k in range(81):
                self.trynum[k] = list(set(self.trynum[k]).intersection(set(self.trynum_help[k])))
            return 2

        if level >= 1:
            # 检查是否在某行/列/九宫格中，有某个数字只有一个可能格子，如果有直接填上
            for k in ['r', 'c', 's']:
                count = count + self._helpByType(m0 = m0, type = k)


        if level >= 2:
            # 唯一性查找
            for k in range(81):
                if(len(m0[k])) == 1:
                    count = count + 1
                    self.arr[k // 9, k % 9] = m0[k][0]
                    self.calcarr[k // 9, k % 9] = 2
                    if DEBUG: print("--| level 2, (" + str(k // 9) + ", " + str(k % 9) + ") <- ", m0[k][0])


        trytime = trytime - 1
        if DEBUG: print("-| trytime - 1.")

        if level >= 3 and count == 0:
            if DEBUG: print("-| count = 0, try level 3 test.")
            m1 = copy.deepcopy(m0)
            for k in ['r', 'c', 's']:
                self._checkMultiNumByType(m0, type = k)
            self.trynum_help = m0.copy()
            if not operator.eq(m1, m0):
                if DEBUG: print("-| level 3 worked, count + 1, trytime + 0.")
                count = count + 1
            else:
                if DEBUG: print("-| level 3 did not work.")

        if level >= 4 and count == 0:
            iter = iter + 1
            if DEBUG: print("-| count = 0, try level 4 test.")
            arr1 = self.arr.copy()
            m0 = copy.deepcopy(m0)
            # 选择首个二元格子，如果没有二元的就随便选一个格子
            # 迭代反正最高也就81层
            f2grid = False
            for k in range(81):
                if len(m0[k]) == 2:
                    f2grid = True
                    break

            if f2grid:
                str0 = s0 + " -> (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][0])
                if DEBUG: print("--| grid selected: (" + str(k // 9) + ", " + str(k % 9) +"), " + str(m0[k]) + " 0: " + str(m0[k][0]))
                    
                # 把格子填上首个待选
                self.arr[k // 9, k % 9] = int(m0[k][0])
                r = self.help(level = 4, trytime = trytime, s0 = str0, iter = iter)
                if r == -1:
                    # 首个不对
                    # 则该路径下另一个正确（在之前的条件下。实际上可能两个都不对）
                    if DEBUG: print("--| level 4 try result: (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][1]) + "(s0:" + s0 + ")")
                    self.arr = arr1
                    self.arr[k // 9, k % 9] = m0[k][1]
                    self.help(init = True)
                    str0 = s0 + " -> (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][1])
                    r1 = self.help(level = 4, trytime = trytime, s0 = str0, iter = iter)
                    if r1 == -1: 
                        if DEBUG: print("--| lv.4 try result: (" + str(k // 9) + ", " + str(k % 9) + ") = NULL (s0:" + s0 + ")")
                        self.trynum_help = m0
                        self.arr = arr1
                        return -1
            else:
                f3grid = False
                for k in range(81):
                    if len(m0[k]) == 3:
                        f3grid = True
                        break
                if f3grid:
                    str0 = s0 + " -> (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][0])
                    if DEBUG: print("--| grid selected (3): (" + str(k // 9) + ", " + str(k % 9) +"), " + str(m0[k]))
                    # 把格子填上首个待选
                    self.arr[k // 9, k % 9] = int(m0[k][0])
                    r = self.help(level = 4, trytime = trytime, s0 = str0, iter = iter)
                    if r == -1:
                        # 首个不对
                        # 则选路径下第二个
                        if DEBUG: print("--| lv.4 try (3): (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][1]) + "(s0:" + s0 + ")")
                        self.arr = arr1.copy()
                        self.arr[k // 9, k % 9] = m0[k][1]
                        self.help(init = True)
                        str0 = s0 + " -> (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][1])
                        r1 = self.help(level = 4, trytime = trytime, s0 = str0, iter = iter)
                        if r1 == -1:
                            # 第二个不对
                            # 则选路径下第三个
                            if DEBUG: print("--| lv.4 try result: (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][2]) + "(s0:" + s0 + ")")
                            self.arr = arr1.copy()
                            self.arr[k // 9, k % 9] = m0[k][1]
                            self.help(init = True)
                            str0 = s0 + " -> (" + str(k // 9) + ", " + str(k % 9) + ") = " + str(m0[k][2])
                            r2 = self.help(level = 4, trytime = trytime, s0 = str0, iter = iter)
                            if r2 == -1: 
                                # 第3个也不对
                                if DEBUG: print("--| lv.4 try result: (" + str(k // 9) + ", " + str(k % 9) + ") = NULL (s0:" + s0 + ")")
                                self.trynum_help = m0
                                self.arr = arr1
                                return -1



        if not init and not tryOnly:
            if trytime <= 0 or self.checkWin() or count == 0: # 没有次数/已经做完/没有新增
                if DEBUG: print("iter = " + str(iter))
                if DEBUG: print("Help: END. trytime = " + str(trytime) + ", self.checkWin() = " + str(self.checkWin()) + ", count = ", str(count))
                if len(self.trynum_help) == self.trynum_help.count([]) and len(self.trynum_help) != 0: return -1
                return 0
            else:
                return self.help(level = level, s0 = s0, trytime = trytime, init = False, tryOnly = False)

        


    def changeTryNum(self, i, j, num, isPrint = True):
        n = i * 9 + j
        if num in self.trynum[n]:
            print("(" + str(i) + ", " + str(j) + "): pencil.remove " + str(num))
            self.trynum[n].remove(num)
        else:
            print("(" + str(i) + ", " + str(j) + "): pencil.append " + str(num))
            self.trynum[n].append(num)



# 背景

def drawBackground(gridSize = defaultGridSize):
    g = gridSize
    # white background
    screen.fill(cols['white'])

    # 细实线
    for j in [1, 2, 4, 5, 7, 8]:
        pygame.draw.line(screen, cols['grey'], [g * j, g * 2], [g * j, g * 11], 3)
        pygame.draw.line(screen, cols['grey'], [g * 0, g * (2 + j)], [g * 9, g * (2 + j)], 3)

    # 数独框
    # 粗实线
    pygame.draw.rect(screen, cols['black'], [0, g * 2, g * 9, g * 9], 5)
    pygame.draw.line(screen, cols['black'], [g * 3, g * 2], [g * 3, g * 11], 5)
    pygame.draw.line(screen, cols['black'], [g * 6, g * 2], [g * 6, g * 11], 5)
    pygame.draw.line(screen, cols['black'], [g * 0, g * 5], [g * 9, g * 5], 5)
    pygame.draw.line(screen, cols['black'], [g * 0, g * 8], [g * 9, g * 8], 5)

    # 上，下，右框线
    pygame.draw.rect(screen, cols['black'], [0, 0, g * 12, g * 2], 5)
    pygame.draw.rect(screen, cols['black'], [g * 9, g * 2, g * 3, g * 9], 5)
    # pygame.draw.rect(screen, cols['black'], [0, g * 11, g * 12, g * 4], 5)

def drawGrid0(j, i, gridSize = defaultGridSize, col = cols['blue1']): # 画出某个格子，i表示x，j表示y，与下面这个是反过来的
    g = gridSize
    pygame.draw.rect(screen, col, 
        [0 + j * g + 3.5, i * g + 3.5, g - 5, g - 5])

def drawGrid(i, j, gridSize = defaultGridSize, col = cols['blue1']): # 画出某个九宫格格子，i和j分别是行列
    g = gridSize
    if i >= 0 and j >= 0 and i < 9 and j < 9: 
        pygame.draw.rect(screen, col, 
        [0 + j * g + 3.5, 2 * g + i * g + 3.5, g - 5, g - 5]) # 未选中将设置i = j = -1

def drawGridOriginal(obj, gridSize = defaultGridSize): #
    a0 = obj.array0
    for i in range(9):
        for j in range(9):
            if a0[i, j] != 0:
                drawGrid(gridSize = gridSize, i = i, j = j, col = cols['grey90'])

def drawGridSelected(i, j): # 画出选中格子
    drawGrid(i = i, j = j, col = (161, 246, 255, 255))

def getNumColor(i, j, obj): #字体颜色
    # 0: 正常 1：错误 2：自动填写 3：自动填写发现错误
    z = {0:'black', 1:'red', 2:'blue', 3:'purple'}
    return z[obj.colarr[(i, j)]]

def drawText(text, col, x, y, type = 1):
    if type == 1:
        t0 = fontNum.render(text, True, col)
    elif type == 2:
        t0 = fontTryNum.render(text, True, col)
    screen.blit(t0, (x, y))

def drawNumber(obj, gridSize = defaultGridSize): # 画数字
    for i in range(9):
        for j in range(9):
            # color
            _color = getNumColor(i, j, obj)
            # text: 0不显示，否则正常打印
            text = str(int(obj.arr[(i, j)]))
            if obj.arr[(i, j)] == 0: text = ""
            x, y = (j + 1 / 4) * gridSize, (i + 2 + 1 / 20) * gridSize
            drawText(text, cols[_color], x, y)

def drawNumberLeft(obj, gridSize = defaultGridSize): # 画出剩下的数字
    g = gridSize
    a = obj.arr.flatten()
    for k in range(9):
        # 画出1个灰方格，一个更浅的灰方格，数字，剩余数量
        # 如果剩余数量 = 0，把灰色加深
        # 如果剩余数量 < 0，把数量变成红色
        kleft = 9 - sum(a == k + 1) # k + 1的剩余数量
        if kleft > 0:
            drawGrid0(0.7 + k * 1.2, 11.9, col = cols['grey80'])
            drawGrid0(0.7 + k * 1.2, 13.1, col = cols['grey' + str(100 - 2 * kleft)])
            drawText(str(k + 1), cols['black'], (0.7 + k * 1.2 + 1 / 4) * g, (11.9 + 1 / 20) * g)
            drawText(str(kleft), cols['black'], (0.7 + k * 1.2 + 1 / 4) * g, (13.1 + 1 / 20) * g)
        elif kleft == 0:
            drawGrid0(0.7 + k * 1.2, 11.9, col = cols['grey80'])
            drawGrid0(0.7 + k * 1.2, 13.1, col = cols['grey100'])
            drawText(str(k + 1), cols['black'], (0.7 + k * 1.2 + 1 / 4) * g, (11.9 + 1 / 20) * g)
            drawText(str(kleft), cols['black'], (0.7 + k * 1.2 + 1 / 4) * g, (13.1 + 1 / 20) * g)
        elif kleft < 0:
            drawGrid0(0.7 + k * 1.2, 11.9, col = cols['grey80'])
            drawGrid0(0.7 + k * 1.2, 13.1, col = cols['grey80'])
            drawText(str(k + 1), cols['black'], (0.7 + k * 1.2 + 1 / 4) * g, (11.9 + 1 / 20) * g)
            drawText(str(kleft), cols['red'], (0.7 + k * 1.2 + 1 / 6) * g, (13.1 + 1 / 30) * g)

def drawSmallNumber(i, j, num, gridSize = defaultGridSize): # 画出某个i行j列格子上的尝试数
    g = gridSize
    num = num - 1
    x = j * g + (num % 3) * g / 3 + 1 / 9 * g
    y = (i + 2) * g + (num // 3) * g / 3 + 1 / 20 * g
    text = str(num + 1)
    if num == -1: text = ""
    drawText(text, cols['grey50'], x, y, type = 2)


def drawTryNumber(obj, gridSize = defaultGridSize): #画出试错数
    g = gridSize
    a = obj.arr.flatten()
    tnum = obj.trynum
    for j in range(81):
        if a[j] != 0 or len(tnum[j]) == 0: 
            continue
        for k in tnum[j]:
            drawSmallNumber(j // 9, j % 9, k)

class clickBtn(object): 
    def __init__(self, x, y, xlen, ylen, label, text = 'test', fontsize = int(defaultGridSize / 3 * 2 - 3), g = defaultGridSize, 
        col1 = cols['grey80'], col2 = cols['grey40'], col3 = cols['grey60']):
        self.x, self.y = x, y
        self.g = g
        self.xlen, self.ylen = xlen, ylen
        self.label = label # 唯一标识符
        self.text = text
        self.fontsize = fontsize
        self.font = pygame.font.SysFont('Times', fontsize)
        self.downcol = col2 # 点下去的颜色
        self.oncol = col3 # 选中的颜色
        self.offcol = col1 # 未选中的颜色
        self.cols = [self.offcol, self.oncol, self.downcol]
        self.status = 0 # 按钮状态，0表示未选中，1表示选中, 2表示点下去

    def on(self):
        s = self.status
        d = len(self.text) / 4
        pygame.draw.rect(screen, self.cols[s], [self.x, self.y, self.xlen, self.ylen]) # btn
        x = self.x + self.xlen / 2 - d * self.g / 2
        y = self.y + 1 / 20 * self.g + (self.ylen - self.g) / 2
        screen.blit(self.font.render(self.text, True, cols['black']), (x, y))

    def selected(self, x, y):
        return (self.x < x and self.y < y and self.x + self.xlen > x and self.y + self.ylen > y)


class clickBtnList(object): 
    def __init__(self, btnList):
        self.btnList = btnList
        self.btnNum = len(btnList)
        self.btnLabel = []
        for k in btnList: self.btnLabel.append(k.label)
        if len(set(self.btnLabel)) != self.btnNum: 
            raise Exception("Click button labels are not unique!")

    def on(self):
        for k in self.btnList: k.on()

    def getSelectBtn(self, x, y): # 获取位置(x,y)对应的按钮序号，没有返回-1
        for k in range(self.btnNum):
            if self.btnList[k].selected(x, y): return k
        return -1

    def getSelectBtnLabel(self, x, y):
        n = self.getSelectBtn(x, y)
        if n == -1: 
            return 
        return self.btnLabel[n]

    def setBtnStatus(self, btnNum, status):
        self.btnList[btnNum].status = status

    def setBtnStatusByLabel(self, label, status):
        self.btnList[self.btnLabel.index(label)].status = status

    def setMultiBtnStatus(self, btnNum, status):
        for k in btnNum:
            self.btnList[k].status = status

    def setMultiBtnStatusByLabel(self, label, status):
        for k in label:
            self.btnList[self.btnLabel.index(k)].status = status

    def setOtherBtnStatus(self, btnNum, status):
        for k in range(self.btnNum):
            if k != btnNum: 
                self.btnList[k].status = status

    def getBtnNumByStatus(self, status):
        r = []
        for k in range(self.btnNum):
            if self.btnList[k].status == status: r.append(k)
        return r

    def getBtnLabelByStatus(self, status):
        r = []
        for k in self.btnList:
            if k.status == status: r.append(k.label)
        return r



def baseConst(gridSize = defaultGridSize):
    a = gridSize # grid size
    b = [a * 12, a * 15] # screen size
    c = int(a - 5)
    d = int(c / 3 - 1)
    return a, b, c, d

def refresh():
    drawBackground()
    drawGridOriginal(obj = sudokuGame)
    drawGridSelected(i = cur_i, j = cur_j)
    drawNumber(obj = sudokuGame)
    drawTryNumber(obj = sudokuGame)
    drawNumberLeft(obj = sudokuGame)
    btnList.on()
    pygame.display.flip()

if __name__ == "__main__":

    # init pygame
    clock = pygame.time.Clock()
    pygame.init()
    print("----------------------------------------------------------")
    
    # contant

    gridSize, screenSize, fontsize, smallFontsize = baseConst()
    g = gridSize
    fontNum = pygame.font.SysFont('Times', fontsize)
    fontTryNum = pygame.font.SysFont('Times', smallFontsize)
    
    # create screen 
    screen = pygame.display.set_mode(screenSize)
    
    # variable parameter
    cur_i, cur_j = -1, -1
    last_i, last_j = -1, -1
    cur_change_size = 0

    # btn list
    mode1btn = clickBtn(9.5 * g, 2.5 * g, 2 * g, 1 * g, text = 'Pen', label = 'pen')
    mode1btn.status = 1
    mode2btn = clickBtn(9.5 * g, 4 * g, 2 * g, 1 * g, text = 'Pencil', label = 'pencil')
    delbtn = clickBtn(9.5 * g, 5.5 * g, 2 * g, 1 * g, text = 'X', label = 'del')
    newbtn = clickBtn(9.5 * g, 7 * g, 2 * g, 1 * g, text = 'New', label = 'new')

    btnList = clickBtnList([mode1btn, mode2btn, delbtn, newbtn])

    # game

    sudokuGame = sudoku()
    
    # main loop
    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print(">>> Quit Game.")
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 获取位置，判断是按在游戏区/按钮
                x, y = event.pos
                cur_j0,cur_i0 = (x / gridSize) , (y / gridSize) - 2 # i, j表示行和列
                if 0 < cur_i0 and cur_i0 < 9 and 0 < cur_j0 and cur_j0 < 9: 
                    cur_i = cur_i0
                    cur_j = cur_j0
                    cur_i, cur_j = int(cur_i), int(cur_j)
                    if DEBUG: print("Current selected grid: (" + str(cur_i) + ", " + str(cur_j) + ")")
                elif btnList.getSelectBtn(x, y) != -1:
                    n = btnList.getSelectBtn(x, y)
                    btnList.setBtnStatus(n, 2)
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                curbtnlabel = btnList.getSelectBtnLabel(x, y)
                if curbtnlabel == 'del':
                    if 'pen' in btnList.getBtnLabelByStatus(1):
                        sudokuGame.arr = sudokuGame.array0.copy()
                        btnList.setBtnStatusByLabel(label = 'del', status = 0)
                    elif 'pencil' in btnList.getBtnLabelByStatus(1):
                        sudokuGame.trynum = emptyList(81)
                        btnList.setBtnStatusByLabel(label = 'del', status = 0)
                elif curbtnlabel in ['pen', 'pencil']:
                    btnList.setMultiBtnStatusByLabel(label = ['pen', 'pencil'], status = 0)
                    btnList.setBtnStatusByLabel(label = curbtnlabel, status = 1)
                elif curbtnlabel == 'new':
                    sudokuGame = sudoku(s = getSudokuByLib(selectNum = -1, seed = time.time())[0])
                    btnList.setBtnStatusByLabel(label = 'new', status = 0)


            elif event.type == pygame.KEYUP:
                if sudokuGame.array0[(cur_i,cur_j)] == 0:
                    if chr(event.key) in ['1','2','3','4','5','6','7','8','9']: # 输入数字
                        if 0 in btnList.getBtnNumByStatus(1): # Pen
                            sudokuGame.arr[(cur_i, cur_j)] = int(chr(event.key))
                            if DEBUG: print("Player sudokuGame.arr: (" + str(cur_i) + ", " + str(cur_j) + ") <- ", int(chr(event.key)))
                            _temp = sudokuGame.checkAll()
                        elif 1 in btnList.getBtnNumByStatus(1): # Pencil
                            sudokuGame.changeTryNum(cur_i, cur_j, int(chr(event.key)))

                    elif chr(event.key) in ['0', '\b']: # 删除数字
                        sudokuGame.arr[(cur_i, cur_j)] = 0
                        if DEBUG: print("Player sudokuGame.arr: (" + str(cur_i) + ", " + str(cur_j) + ") <- ", 0)
                        _temp = sudokuGame.checkAll()
                    elif chr(event.key) in ['t']: # 测试，test, 
                        sudokuGame.help(level = 4) # 此处测试lv.4的帮助
                    elif chr(event.key) in ['y']:
                        sudokuGame.help(level = 3) # level=3的help
                    elif chr(event.key) in ['h']: # 2级帮助：直至无法继续帮助为止
                        sudokuGame.help(level = 2)
                    elif chr(event.key) in ['r']: # 2级帮助：1次
                        sudokuGame.help(level = 2, trytime = 1)
                    elif chr(event.key) in ['n']: # 仅进行检查
                        sudokuGame.help(level = 2,  tryOnly = True)
                    elif chr(event.key) in ['m']: # 使用电脑检测数据
                        sudokuGame.help(level = 2,  tryOnly = True)
                        sudokuGame.trynum = sudokuGame.trynum_help.copy()
                    elif chr(event.key) in ['d']: # 删除所有草稿
                        sudokuGame.trynum = emptyList(81)
                    elif chr(event.key) in ['i']: # 重置电脑草稿
                        sudokuGame.help(init = True)

        drawBackground()
        drawGridOriginal(obj = sudokuGame)
        drawGridSelected(i = cur_i, j = cur_j)
        drawNumber(obj = sudokuGame)
        drawTryNumber(obj = sudokuGame)
        drawNumberLeft(obj = sudokuGame)
        btnList.on()


        pygame.display.flip()
        # check win or not
    
    pygame.quit()
