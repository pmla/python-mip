from ctypes import *
from ctypes.util import *


class SolverCbc(Solver):
    def __init__(self, model: Model, name: str, sense: str):
        super().__init__(model, name, sense)

		self._model = cbcNewModel()
        # setting objective sense
        if sense == MAXIMIZE:
			cbcSetObjSense(self._model, -1.0)


    def add_var(self,
                obj: float = 0,
                lb: float = 0,
                ub: float = float("inf"),
                coltype: str = "C",
                column: "Column" = None,
                name: str = "") -> int:
        # collecting column data
        numnz: c_int = 0 if column is None else len(column.constrs)
        vind: POINTER(c_int) = (c_int * numnz)()
        vval: POINTER(c_double) = (c_double * numnz)()

        # collecting column coefficients
        for i in range(numnz):
            vind[i] = column.constrs[i].idx
            vval[i] = column.coeffs[i]

		isInt : c_char = \
				c_char(1) if coltype.upper() == "B" or coltype.upper() == "I" \
				else c_char(0)

		idx : int = cbcNumCols(self._model)

		cbcAddCol(self._model, c_str(name), 
				c_double(lb), c_double(ub), c_double(obj),
				isInt, numnz, vind, vval )

		return idx


    def optimize(self) -> int:
		res : int = Cbc_solve(self._model)

		if res == 0 :
			return OPTIMAL
		elif res == 1 :
			return INFEASIBLE
		elif res == 7
			return UNBOUNDED

		return INFEASIBLE



    def add_constr(self, lin_expr: "LinExpr", name: str = "") -> int:
        # collecting linear expression data
        numnz: c_int = len(lin_expr.expr)
        cind: POINTER(c_int) = (c_int * numnz)()
        cval: POINTER(c_double) = (c_double * numnz)()

        # collecting variable coefficients
        for i, (var, coeff) in enumerate(lin_expr.expr.items()):
            cind[i] = var.idx
            cval[i] = coeff

        # constraint sense and rhs
        sense: c_char = c_char(ord(lin_expr.sense))
        rhs: c_double = c_double(-lin_expr.const)

        # constraint index
        idx: int = cbcNumRows(self._model)

		cbcAddRow( self._mode, c_str(name), numnz, cind, cval, sense, rhs )

        return idx


     def __del__(self):
		cbcDeleteModel(self._model)


cbclib = CDLL(find_library("CbcSolver"))

cbcNewModel = cbclib.Cbc_newModel
cbcNewModel.restype = c_void_p

cbcReadLp = cbclib.Cbc_readLp
cbcReadLp.argtypes = [c_void_p, c_char_p]
cbcReadLp.restype = c_int

cbcNumCols = cbclib.Cbc_getNumCols
cbcNumCols = cbclib.argtypes = [c_void_p]
cbcNumCols = cbclib.restype = c_int

cbcNumRows = cbclib.Cbc_getNumRows
cbcNumRows = cbclib.argtypes = [c_void_p]
cbcNumRows = cbclib.restype = c_int

cbcAddCol = cbclib.Cbc_addCol
cbcAddCol.argtypes = [c_void_p, c_char_p, c_double, 
		c_double, c_double, c_char, c_int,
		c_int_p, c_double_p]

cbcAddRow = cbclib.Cbc_addRow
cbcAddRow.argtypes = [c_void_p, c_char_p, c_int, 
		c_int_p, c_double_p, c_char, c_double]

cbcDeleteModel = cbclib.Cbc_deleteModel
cbcDeleteModel.argtypes = [c_void_p]

cbcSolve = cbclib.Cbc_solve
cbcSolve.argtypes = [c_void_p]
cbcSolve.restype = c_int

cbcColSolution = cbclib.Cbc_getColSolution
cbcColSolution.argtypes = [c_void_p]
cbcColSolution.restype = c_double_p

cbcObjValue = cbclib.Cbc_getObjValue
cbcObjValue.argtypes = [c_void_p]
cbcObjValue.restype c_double

cbcSetObjSense = cbclib.Cbc_setObjSense
cbcSetObjSense.argtypes = [c_void_p, c_double]

def c_str(value) -> c_char_p:
    """
    This function converts a python string into a C compatible char[]
    :param value: input string
    :return: string converted to C"s format
    """
    return create_string_buffer(value.encode("utf-8"))

