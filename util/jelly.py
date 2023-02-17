class Jelly:
    """
    A class for pickling and unpickling instances of itself
    """

    # auther: hsn
    # data: 01/15/2023(MM/DD/YYYY)
    # ver: 2.0
    def __init__(self):
        self._var_init()

    def _var_init(self):
        # Initialize instance variables
        ...

    def _get_instance_variables(self) -> list:
        """
        Get a list of all non-method instance variables
        """
        return [i for i in dir(self) if not i.startswith('__') and not callable(getattr(self, i))]

    def __getstate__(self):
        """
        Get the state of the object for pickling
        """
        state = {k: getattr(self, k) for k in self._get_instance_variables()}
        return state

    def __setstate__(self, state):
        """
        Set the state of the object after unpickling
        """
        state = state
        self._var_init()
        for k, v in state.items():
            setattr(self, k, v)
