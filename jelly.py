
class Jelly:
    # auther: hsn
    # data: 01/15/2023(MM/DD/YYYY)
    # ver: 1.0
    def __init__(self):
        self._var_init()

    def _var_init(self):
        ...

    def _get_self_var(self) -> list:
        rt_l = []
        [rt_l.append(i)
         if (not i.startswith('__')) and (type(getattr(self, i)).__name__ != 'method')
         else None
         for i in dir(self)]
        return rt_l

    def __getstate__(self):
        return {k: getattr(self, k) for k in self._get_self_var()}

    def __setstate__(self, state):
        self._var_init()
        for k in state:
            setattr(self, k, state[k])
