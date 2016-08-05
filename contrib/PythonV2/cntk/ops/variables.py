import numpy as np
from cntk import cntk_py
from cntk import DATATYPE
from cntk.graph import TensorOpsMixin
from .. import utils
from cntk.context import get_context

def _sanitize_value(shape, value, dtype, dev):
    np_dtype = utils.sanitize_dtype_numpy(dtype)
    cntk_dtype  = utils.sanitize_dtype_cntk(dtype)
    if value is None:
        if shape is None:
            raise ValueError('you need to specify at least shape or value')

        if not np.isscalar(shape):
            # cntk uses column major, thus we reverse the shape    
            shape = tuple(reversed(shape))

        ndav = utils.create_NDArrayView(shape, cntk_dtype, dev)

    else:
        if not isinstance(value, np.ndarray) or value.dtype!=np_dtype:
            value = np.asarray(value, dtype=np_dtype)

        ndav = utils.create_NDArrayView_from_NumPy(value, dev)

    return ndav

class Variable(cntk_py.Variable, TensorOpsMixin):
    def __init__(self, shape=None, data_type=None, needs_gradient=True, name=''):
        if data_type is None:            
            data_type = str(np.float32)
        dtype = utils.sanitize_dtype_cntk(data_type)
        super(Variable, self).__init__(shape, dtype, needs_gradient, name)

class Parameter(cntk_py.Parameter, TensorOpsMixin):
    def __init__(self, shape=None, value=None, data_type=None, dev=None, name=''):
        
        if data_type is None:
            if not isinstance(value, np.ndarray):        
                data_type = str(np.float32)
            else:
                data_type = str(value.dtype)        

        if not dev:
            dev = cntk_py.DeviceDescriptor_CPUDevice()

        ndav = _sanitize_value(shape, value, data_type, dev)
        super(Parameter, self).__init__(ndav, name)

class Constant(cntk_py.Constant, TensorOpsMixin):
    def __init__(self, shape=None, value=None, data_type=None, dev=None, name=''):

        if data_type is None:
            if not isinstance(value, np.ndarray):        
                data_type = str(np.float32)
            else:
                data_type = str(value.dtype)     

        if not dev:
            dev = cntk_py.DeviceDescriptor_CPUDevice()            

        ndav = _sanitize_value(shape, value, data_type, dev)
        super(Constant, self).__init__(ndav, name)

def constant_from_scalar(shape=None, value=None, data_type=None, dev=None, name=''):
    if not dev:
        dev = cntk_py.DeviceDescriptor_CPUDevice()            

    if data_type is None:
        if not isinstance(value, np.ndarray):        
            data_type = str(np.float32)
        else:
            data_type = str(value.dtype)     

    dtype = utils.sanitize_dtype_cntk(data_type)

    if not shape:
        shape = ()
    if dtype == cntk_py.DataType_Float:
        return cntk_py.ConstantFloat(shape, value, dev, name)
    elif dtype == cntk_py.DataType_Double:
        return cntk_py.ConstantDouble(shape, value, dev, name)
    raise ValueError('unrecognized data_type: %s', dtype)

class Placeholder(cntk_py.Placeholder, TensorOpsMixin):
    def __init__(self, shape=None, data_type=None, name=''):
        if data_type is None:            
            data_type = str(np.float32)
        dtype = utils.sanitize_dtype_cntk(data_type)
        Variable.__init__(self, shape, dtype, name)
