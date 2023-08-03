import simpy
import random

class school:
    def __init__(self, env):
        self.env = env
        self.class_end = env.event()
        self.class_test = env.event()
        self.core_num = 8
        self.pupil_event = [env.event() for i in range(self.core_num)]
        self.pupil_procs = [env.process(self.pupil(i)) for i in range(self.core_num)]
        self.bell_procs = env.process(self.bell())

    def bell(self):
        for i in range(20):
            yield self.env.timeout(45)
            self.class_end.succeed()
            self.class_end = self.env.event()
            print()
            rett = yield simpy.AnyOf(env, self.pupil_event + [self.class_test])
            ret_list = [ret_value for ret_id, ret_value in rett.items()]
            print( ret_list )

    def pupil(self, id):
        while 1:
            yield self.class_end
            if random.random() < 0.5:
                self.pupil_event[id].succeed("{0}".format(id))
                self.pupil_event[id] = self.env.event()


env = simpy.Environment()
school = school(env)
env.run()