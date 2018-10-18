__author__ = 'Daen'


class CheckLimits:

    def GELE(self, number_value, number_low, number_high):
        if (number_value >= number_low) and (number_value <= number_high):
            return True
        else:
            return False

    def EQ(self, number_value, number_low):
        if number_value == number_low:
            return True
        else:
            return False

    def NE(self, number_value, number_low):
        if number_value != number_low:
            return True
        else:
            return False

    def PCT(self, number_value, number_low, scale):
        __max_value = number_low * (1 + scale / 100)
        __min_value = number_low * (1 - scale / 100)

        if (number_value < __max_value) and (number_value > __min_value):
            return True
        else:
            return False


class TrigMethod:

    signal_list = list
    __signal_status = []
    __signal_result = []

    def init(self, signal_amount=1):
        self.__signal_status = [0 for i in range(signal_amount)]
        self.__signal_result = [0 for i in range(signal_amount)]

    def one_shot(self, number_signal, boolean_option=1):
        if boolean_option == 1:
            if (self.signal_list[number_signal] ^ self.__signal_status[number_signal]) & self.signal_list[number_signal]:

                self.__signal_result[number_signal] = 1
            else:
                self.__signal_result[number_signal] = 0
        if boolean_option == 0:
            if (self.signal_list[number_signal] ^ self.__signal_status[number_signal]) & self.__signal_status[number_signal]:
                self.__signal_result[number_signal] = 0
            else:
                self.__signal_result[number_signal] = 1

        self.__signal_status[number_signal] = self.signal_list[number_signal]

        return self.__signal_result[number_signal]



class SequenceTest:
    __count_pass = 0
    __count_fail = 0
    __result = []
    __sum_step_result = 0

    __step_status = []
    __step_result = []
    __step_status_first = []
    __step_result_first = []
    __step_status_second = []
    __step_result_second = []
    number_count = 1
    number_timeout = 10
    config = [0]
    step_list = [0]
    __sequence_result = ''
    current_step = list
    step_count = list
    for i in range(88):
        print(i)
    def init(self):
        self.__count_fail = 0
        self.__count_pass = 0
        self.__result = [0 for i in range(len(self.config))]
        self.__step_status = [0 for i in range(len(self.config))]
        self.__step_result = [0 for i in range(len(self.config))]
        self.__step_status_first = [0 for i in range(len(self.config))]
        self.__step_result_first = [0 for i in range(len(self.config))]
        self.__step_status_second = [0 for i in range(len(self.config))]
        self.__step_result_second = [0 for i in range(len(self.config))]
        self.__sequence_result = ''
        self.current_step = 0
        self.step_count = 0

    def sequence_test(self):
        if self.current_step == (len(self.step_list)):
            pass
        else:
            if self.config[self.current_step]:

                if self.step_list[self.current_step]:
                    self.__count_pass += 1
                if self.__count_pass >= self.number_count:
                    self.__result[self.current_step] = 1
                    self.__count_fail = 0
                    self.__count_pass = 0
                    if self.current_step == (len(self.step_list) - 1): pass
                    else: self.current_step += 1
                    # print('result:', self.__result)
                    # print('result:', len(self.__result), 'config:', len(self.config), 'step_list:', len(self.step_list))

                    # if self.current_step == 1: self.step_count = 0
                    # else: self.step_count += 1
                    self.step_count += 1
                if self.__count_fail >= self.number_timeout:
                    self.__result[self.current_step] = 0
                    self.__count_fail = 0
                    self.__count_pass = 0
                    self.__sequence_result = 'fail'
                else:
                    self.__count_fail += 1
            else:
                while True:
                    self.__result[self.current_step] = 1
                    self.current_step += 1
                    if self.current_step == (len(self.step_list)):
                        break
                    if self.config[self.current_step]:
                        break
#        print(self.step_count, self.current_step)
        self.__sum_step_result = 0
        for i in range(len(self.__result)):
            self.__sum_step_result += self.__result[i]
        if self.__sum_step_result == len(self.step_list):
            self.__sequence_result = 'pass'

    def step_status(self, step, boolean_option=1):
        if self.config[step]:
            self.__step_status_first[step] = 1 if (self.current_step == step) and self.config[step] else 0

            if boolean_option == 1:
                if (self.__step_status_first[step] ^ self.__step_status_second[step]) & self.__step_status_first[step]:
                    self.__step_status[step] = 1
                else:
                    self.__step_status[step] = 0

            if boolean_option == 0:
                if (self.__step_status_first[step] ^ self.__step_status_second[step]) & self.__step_status_second[step]:
                    self.__step_status[step] = 0
                else:
                    self.__step_status[step] = 1

            self.__step_status_second[step] = self.__step_status_first[step]

            return self.__step_status[step]

    def step_result(self, step, boolean_option=1):
        if self.config[step]:
            self.__step_result_first[step] = 1 if self.__result[step] and self.config[step] else 0
            if boolean_option == 1:
                if (self.__step_result_first[step] ^ self.__step_result_second[step]) & self.__step_result_first[step]:
                    self.__step_result[step] = 1
                else:
                    self.__step_result[step] = 0
            if boolean_option == 0:
                if (self.__step_result_first[step] ^ self.__step_result_second[step]) & self.__step_result_second[step]:
                    self.__step_result[step] = 0
                else:
                    self.__step_result[step] = 1

            self.__step_result_second[step] = self.__step_result_first[step]
            return self.__step_result[step]

    def sequence_pass(self):
        if self.__sequence_result is 'pass':
            return True

    def sequence_fail(self):
        if self.__sequence_result is 'fail':

            return True

