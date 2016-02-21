# Use there to reference static strings
INT_TYPE = "int"
UINT_TYPE = "uint"
FLOAT_TYPE = "float"
STRING_TYPE = "string"
BYTE_TYPE = "byte"
VOID_TYPE = "void"


def raw_method_parser(raw_method):
    arr_m_s = raw_method.splitlines(False)
    methods = []
    for method_str in arr_m_s:
        methods.append(Method(method_str, None))


class Method:
    """
        Method class takes 3 parameters for Constructor
        1. name of the method which is a string
        2. params: which is an array of strings
        2. comm: which contains a method "send" that takes in string data
    """

    def __init__(self, raw_string, comm):
        self.r_type, self.name, self.params = self.parser(raw_string)
        self._send = comm.send

    def __call__(self, *args, **kwargs):
        if len(args) != len(self.params):
            raise AttributeError("expected {} parameters but go {} instead".format(len(args), len(self.params)))
        for i, arg in enumerate(args):
            if type(arg) == self.params.get(i):
                continue
            else:
                raise AttributeError(
                    "{} th argument is of type {} expected {}".format(i + i, type(arg), self.params.get(i)))
        self._send()

    '''
        parser method
        1. takes in a raw string of method
        2. returns return_type, method_name, params
    '''

    @staticmethod
    def parser(raw_string):
        # TODO: implement validator for raw_string

        # extract return type
        r_type, rest = raw_string.split(" ", 1)
        r_type = r_type.strip(" ")

        # extract name of the method
        m_name, rest = rest.split("(", 1)
        m_name = m_name.strip(" ")

        # convert rest string into a string of p_types separated with ","
        rest.strip(" ")
        rest.strip(")")

        # extract the p_types
        p_types = rest.split(",")
        for t in p_types:
            t = t.strip(" ")

        return r_type, m_name, p_types
