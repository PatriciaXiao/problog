from .logic import Constant, Var, Term
from .core import GroundingError


class NonGroundProbabilisticClause(GroundingError) : 
    
    def __init__(self, location=None) :
        self.location = location
        msg = 'Encountered non-ground probabilistic clause' 
        if self.location : msg += ' at position %s:%s' % self.location
        msg += '.'
        GroundingError.__init__(self, msg)

class _UnknownClause(Exception) :
    """Undefined clause in call used internally."""
    pass

class UnknownClause(GroundingError) :
    """Undefined clause in call."""
    
    def __init__(self, signature, location) :
        self.location = location
        msg = "No clauses found for '%s'" % signature
        if location : msg += " at position %s:%s" % location
        msg += '.'
        GroundingError.__init__(self, msg)
        
class ConsultError(GroundingError) :
    
    def __init__(self, message, location=None) :
        self.location = location
        msg = message
        if location : msg += " at position %s:%s" % location
        msg += '.'
        GroundingError.__init__(self, msg)

class UnifyError(Exception) : pass

class VariableUnification(GroundingError) : 
    """The engine does not support unification of two unbound variables."""
    
    def __init__(self, location=None) :
        self.location = location
        GroundingError.__init__(self, 'Unification of unbound variables not supported.')


def unify_value( v1, v2 ) :
    """Test unification of two values and return most specific unifier."""
    
    if is_variable(v1) :
        return v2
    elif is_variable(v2) :
        return v1
    elif v1.signature == v2.signature : # Assume Term
        return v1.withArgs(*[ unify_value(a1,a2) for a1, a2 in zip(v1.args, v2.args) ])
    else :
        raise UnifyError()


class StructSort(object) :
    
    def __init__(self, obj, *args):
        self.obj = obj
    def __lt__(self, other):
        return struct_cmp(self.obj, other.obj) < 0
    def __gt__(self, other):
        return struct_cmp(self.obj, other.obj) > 0
    def __eq__(self, other):
        return struct_cmp(self.obj, other.obj) == 0
    def __le__(self, other):
        return struct_cmp(self.obj, other.obj) <= 0  
    def __ge__(self, other):
        return struct_cmp(self.obj, other.obj) >= 0
    def __ne__(self, other):
        return struct_cmp(self.obj, other.obj) != 0


class CallModeError(GroundingError) :
    
    def __init__(self, functor, args, accepted=[], message=None, location=None) :
        if functor :
            self.scope = '%s/%s'  % ( functor, len(args) )
        else :
            self.scope = None
        self.received = ', '.join(map(self.show_arg,args))
        self.expected = [  ', '.join(map(self.show_mode,mode)) for mode in accepted  ]
        self.location = location
        msg = 'Invalid argument types for call'
        if self.scope : msg += " to '%s'" % self.scope
        if location != None : msg += ' at position %s:%s ' % (location)
        msg += ': arguments: (%s)' % self.received
        if accepted :
            msg += ', expected: (%s)' % ') or ('.join(self.expected) 
        else :
            msg += ', expected: ' + message 
        Exception.__init__(self, msg)
        
    def show_arg(self, x) :
        if x == None :
            return '_'
        else :
            return str(x)
    
    def show_mode(self, t) :
        return mode_types[t][0]


def is_ground( *terms ) :
    """Test whether a any of given terms contains a variable (recursively).
    
    :return: True if none of the arguments contains any variables.
    """
    for term in terms :
        if is_variable(term) :
            return False
        elif not is_ground(*term.args) : 
            return False
    return True

def is_variable( v ) :
    """Test whether a Term represents a variable.
    
    :return: True if the expression is a variable
    """
    return v == None or type(v) == int    

def is_var(term) :
    return is_variable(term) or term.isVar()

def is_nonvar(term) :
    return not is_var(term)

def is_term(term) :
    return not is_var(term) and not is_constant(term)

def is_float_pos(term) :
    return is_constant(term) and term.isFloat()

def is_float_neg(term) :
    return is_term(term) and term.arity == 1 and term.functor == "'-'" and is_float_pos(term.args[0])

def is_float(term) :
    return is_float_pos(term) or is_float_neg(term)

def is_integer_pos(term) :
    return is_constant(term) and term.isInteger()

def is_integer_neg(term) :
    return is_term(term) and term.arity == 1 and term.functor == "'-'" and is_integer_pos(term.args[0])

def is_integer(term) :
    return is_integer_pos(term) or is_integer_neg(term)

def is_string(term) :
    return is_constant(term) and term.isString()

def is_number(term) :
    return is_float(term) and is_integer(term)

def is_constant(term) :
    return not is_var(term) and term.isConstant()

def is_atom(term) :
    return is_term(term) and term.arity == 0

def is_rational(term) :
    return False

def is_dbref(term) :
    return False

def is_compound(term) :
    return is_term(term) and term.arity > 0
    
def is_list_maybe(term) :
    """Check whether the term looks like a list (i.e. of the form '.'(_,_))."""
    return is_compound(term) and term.functor == '.' and term.arity == 2
    
def is_list_nonempty(term) :
    if is_list_maybe(term) :
        tail = list_tail(term)
        return is_list_empty(tail) or is_var(tail)
    return False

def is_fixed_list(term) :
    return is_list_empty(term) or is_fixed_list_nonempty(term)

def is_fixed_list_nonempty(term) :
    if is_list_maybe(term) :
        tail = list_tail(term)
        return is_list_empty(tail)
    return False
    
def is_list_empty(term) :
    return is_atom(term) and term.functor == '[]'
    
def is_list(term) :
    return is_list_empty(term) or is_list_nonempty(term)
    
def is_compare(term) :
    return is_atom(term) and term.functor in ("'<'", "'='", "'>'")

mode_types = {
    'i' : ('integer', is_integer),
    'I' : ('positive_integer', is_integer_pos),
    'v' : ('var', is_var),
    'n' : ('nonvar', is_nonvar),
    'l' : ('list', is_list),
    'L' : ('fixed_list', is_fixed_list),    # List of fixed length (i.e. tail is [])
    '*' : ('any', lambda x : True ),
    '<' : ('compare', is_compare ),         # < = >
    'g' : ('ground', is_ground ),
    'a' : ('atom', is_atom),
    'c' : ('callable', is_term)
}

def check_mode( args, accepted, functor=None, location=None, database=None, **k) :
    for i, mode in enumerate(accepted) :
        correct = True
        for a,t in zip(args,mode) :
            name, test = mode_types[t]
            if not test(a) : 
                correct = False
                break
        if correct : return i
    if database and location :
        location = database.lineno(location)
    else :
        location = None
    raise CallModeError(functor, args, accepted, location=location)
    
def list_elements(term) :
    elements = []
    tail = term
    while is_list_maybe(tail) :
        elements.append(tail.args[0])
        tail = tail.args[1]
    return elements, tail
    
def list_tail(term) :
    tail = term
    while is_list_maybe(tail) :
        tail = tail.args[1]
    return tail
               

def builtin_split_call( term, parts, database=None, location=None, **k ) :
    """T =.. L"""
    functor = '=..'
    # modes:
    #   <v> =.. list  => list has to be fixed length and non-empty
    #                       IF its length > 1 then first element should be an atom
    #   <n> =.. <list or var>
    #
    mode = check_mode( (term, parts), ['vL', 'nv', 'nl' ], functor=functor, **k )
    if mode == 0 :
        elements, tail = list_elements(parts)
        if len(elements) == 0 :
            raise CallModeError(functor, (term,parts), message='non-empty list for arg #2 if arg #1 is a variable', location=database.lineno(location))
        elif len(elements) > 1 and not is_atom(elements[0]) :
            raise CallModeError(functor, (term,parts), message='atom as first element in list if arg #1 is a variable', location=database.lineno(location))
        elif len(elements) == 1 :
            # Special case => term == parts[0]
            return [(elements[0],parts)]
        else :
            T = elements[0](*elements[1:])
            return [ (T , parts) ] 
    else :
        part_list = ( term.withArgs(), ) + term.args
        current = Term('[]')
        for t in reversed(part_list) :
            current = Term('.', t, current)
        try :
            L = unify_value(current, parts)
            elements, tail = list_elements(L)
            term_new = elements[0](*elements[1:])
            T = unify_value( term, term_new )
            return [(T,L)]            
        except UnifyError :
            return []

def builtin_arg(index,term,argument, **k) :
    mode = check_mode( (index,term,arguments), ['In*'], functor='arg', **k)
    index_v = int(index) - 1
    if 0 <= index_v < len(term.args) :
        try :
            arg = term.args[index_v]
            res = unify_value(arg,argument)
            return [(index,term,res)]
        except UnifyError :
            pass
    return []

def builtin_functor(term,functor,arity, **k) :
    mode = check_mode( (term,functor,arity), ['vaI','n**'], functor='functor', **k)
    
    if mode == 0 : 
        callback.newResult( Term(functor, *((None,)*int(arity)) ), functor, arity )
    else :
        try :
            func_out = unify_value(functor, Term(term.functor))
            arity_out = unify_value(arity, Constant(term.arity))
            return [(term, func_out, arity_out)]
        except UnifyError :
            pass
    return []

def builtin_true( **k ) :
    """``true``"""
    return True


def builtin_fail( **k ) :
    """``fail``"""
    return False


def builtin_eq( A, B, **k ) :
    """``A = B``
        A and B not both variables
    """
    if is_var(A) and is_var(B) :
        raise VariableUnification()
    else :
        try :
            R = unify_value(A,B)
            return [( R, R )]
        except UnifyError :
            return []


def builtin_neq( A, B, **k ) :
    """``A \= B``
        A and B not both variables
    """
    if is_var(A) and is_var(B) :
        return False
    else :
        try :
            R = unify_value(A,B)
            return False
        except UnifyError :
            return True
            

def builtin_notsame( A, B, **k ) :
    """``A \== B``"""
    if is_var(A) and is_var(B) :
        raise VariableUnification() # TODO this could work
    # In Python A != B is not always the same as not A == B.
    else :
        return not A == B


def builtin_same( A, B, **k ) :
    """``A == B``"""
    if is_var(A) and is_var(B) :
        raise VariableUnification() # TODO this could work
    else :
        return A == B


def builtin_gt( A, B, **k ) :
    """``A > B`` 
        A and B are ground
    """
    mode = check_mode( (A,B), ['gg'], functor='>', **k )
    return A.value > B.value


def builtin_lt( A, B, **k ) :
    """``A > B`` 
        A and B are ground
    """
    mode = check_mode( (A,B), ['gg'], functor='<', **k )
    return A.value < B.value


def builtin_le( A, B, **k ) :
    """``A =< B``
        A and B are ground
    """
    mode = check_mode( (A,B), ['gg'], functor='=<', **k )
    return A.value <= B.value


def builtin_ge( A, B, **k ) :
    """``A >= B`` 
        A and B are ground
    """
    mode = check_mode( (A,B), ['gg'], functor='>=', **k )
    return A.value >= B.value


def builtin_val_neq( A, B, **k ) :
    """``A =\= B`` 
        A and B are ground
    """
    mode = check_mode( (A,B), ['gg'], functor='=\=', **k )
    return A.value != B.value


def builtin_val_eq( A, B, **k ) :
    """``A =:= B`` 
        A and B are ground
    """
    mode = check_mode( (A,B), ['gg'], functor='=:=', **k )
    return A.value == B.value


def builtin_is( A, B, **k ) :
    """``A is B``
        B is ground
    """
    mode = check_mode( (A,B), ['*g'], functor='is', **k )
    try :
        R = Constant(B.value)
        unify_value(A,R)
        return [(R,B)]
    except UnifyError :
        return []


def builtin_var( term, **k ) :
    return is_var(term)


def builtin_atom( term, **k ) :
    return is_atom(term)


def builtin_atomic( term, **k ) :
    return is_atom(term) or is_number(term)


def builtin_compound( term, **k ) :
    return is_compound(term)


def builtin_float( term, **k ) :
    return is_float(term)


def builtin_integer( term, **k ) :
    return is_integer(term)


def builtin_nonvar( term, **k ) :
    return not is_var(term)


def builtin_number( term, **k ) :
    return is_number(term) 


def builtin_simple( term, **k ) :
    return is_var(term) or is_atomic(term)
    

def builtin_callable( term, **k ) :
    return is_term(term)


def builtin_rational( term, **k ) :
    return is_rational(term)


def builtin_dbreference( term, **k ) :
    return is_dbref(term)  
    

def builtin_primitive( term, **k ) :
    return is_atomic(term) or is_dbref(term)


def builtin_ground( term, **k ) :
    return is_ground(term)


def builtin_is_list( term, **k ) :
    return is_list(term)

def compare(a,b) :
    if a < b :
        return -1
    elif a > b :
        return 1
    else :
        return 0
    
def struct_cmp( A, B ) :
    # Note: structural comparison
    # 1) Var < Num < Str < Atom < Compound
    # 2) Var by address
    # 3) Number by value, if == between int and float => float is smaller (iso prolog: Float always < Integer )
    # 4) String alphabetical
    # 5) Atoms alphabetical
    # 6) Compound: arity / functor / arguments
        
    # 1) Variables are smallest
    if is_var(A) :
        if is_var(B) :
            # 2) Variable by address
            return compare(A,B)
        else :
            return -1
    elif is_var(B) :
        return 1
    # assert( not is_var(A) and not is_var(B) )
    
    # 2) Numbers are second smallest
    if is_number(A) :
        if is_number(B) :
            # Just compare numbers on float value
            res = compare(float(A),float(B))
            if res == 0 :
                # If the same, float is smaller.
                if is_float(A) and is_integer(B) : 
                    return -1
                elif is_float(B) and is_integer(A) : 
                    return 1
                else :
                    return 0
        else :
            return -1
    elif is_number(B) :
        return 1
        
    # 3) Strings are third
    if is_string(A) :
        if is_string(B) :
            return compare(str(A),str(B))
        else :
            return -1
    elif is_string(B) :
        return 1
    
    # 4) Atoms / terms come next
    # 4.1) By arity
    res = compare(A.arity,B.arity)
    if res != 0 : return res
    
    # 4.2) By functor
    res = compare(A.functor,B.functor)
    if res != 0 : return res
    
    # 4.3) By arguments (recursively)
    for a,b in zip(A.args,B.args) :
        res = struct_cmp(a,b)
        if res != 0 : return res
        
    return 0

    
def builtin_struct_lt(A, B, **k) :
    return struct_cmp(A,B) < 0    

    
def builtin_struct_le(A, B, **k) :
    return struct_cmp(A,B) <= 0

    
def builtin_struct_gt(A, B, **k) :
    return struct_cmp(A,B) > 0

    
def builtin_struct_ge(A, B, **k) :
    return struct_cmp(A,B) >= 0


def builtin_compare(C, A, B, **k) :
    mode = check_mode( (C,A,B), [ '<**', 'v**' ], functor='compare', **k)
    compares = "'>'","'='","'<'" 
    c = struct_cmp(A,B)
    c_token = compares[1-c]
    
    if mode == 0 : # Given compare
        if c_token == C.functor : return [ (C,A,B) ]
    else :  # Unknown compare
        return [ (Term(c_token), A, B ) ]
    
# numbervars(T,+N1,-Nn)    number the variables TBD?

def build_list(elements, tail) :
    current = tail
    for el in reversed(elements) :
        current = Term('.', el, current)
    return current


def builtin_length(L, N, **k) :
    mode = check_mode( (L,N), [ 'LI', 'Lv', 'lI', 'vI' ], functor='length', **k)
    # Note that Prolog also accepts 'vv' and 'lv', but these are unbounded.
    # Note that lI is a subset of LI, but only first matching mode is returned.
    if mode == 0 or mode == 1 :  # Given fixed list and maybe length
        elements, tail = list_elements(L)
        list_size = len(elements)
        try :
            N = unify_value(N, Constant(list_size))
            return [ ( L, N ) ]
        except UnifyError :
            return []    
    else :    # Unbounded list or variable list and fixed length.
        if mode == 2 :
            elements, tail = list_elements(L)
        else :
            elements, tail = [], L
        remain = int(N) - len(elements)
        if remain < 0 :
            raise UnifyError()
        else :
            extra = [None] * remain
        newL = build_list( elements + extra, Term('[]'))
        return [ (newL, N)]



def builtin_sort( L, S, **k ) :
    # TODO doesn't work properly with variables e.g. gives sort([X,Y,Y],[_]) should be sort([X,Y,Y],[X,Y])
    mode = check_mode( (L,S), [ 'L*' ], functor='sort', **k )
    elements, tail = list_elements(L)  
    # assert( is_list_empty(tail) )
    try :
        sorted_list = build_list(sorted(set(elements), key=StructSort), Term('[]'))
        S_out = unify_value(S,sorted_list)
        return [(L,S_out)]
    except UnifyError :
        return []


def builtin_between( low, high, value, **k ) :
    mode = check_mode((low,high,value), [ 'iii', 'iiv' ], functor='between', **k)
    low_v = int(low)
    high_v = int(high)
    if mode == 0 : # Check    
        value_v = int(value)
        if low_v <= value_v <= high_v :
            return [(low,high,value)]
    else : # Enumerate
        results = []
        for value_v in range(low_v, high_v+1) :
            results.append( (low,high,Constant(value_v)) ) 
        return results


def builtin_succ( a, b, **k ) :
    mode = check_mode((a,b), [ 'vI', 'Iv', 'II' ], functor='succ', **k)
    if mode == 0 :
        b_v = int(b)
        return [(Constant(b_v-1), b)]
    elif mode == 1 :
        a_v = int(a)
        return [(a, Constant(a_v+1))]
    else :
        a_v = int(a)
        b_v = int(b)
        if b_v == a_v + 1 :
            return [(a, b)]
    return []


def builtin_plus( a, b, c , **k) :
    mode = check_mode((a,b,c), [ 'iii', 'iiv', 'ivi', 'vii' ], functor='plus', **k)
    if mode == 0 :
        a_v = int(a)
        b_v = int(b)
        c_v = int(c)
        if a_v + b_v == c_v :
            return [(a,b,c)]
    elif mode == 1 :
        a_v = int(a)
        b_v = int(b)
        return [(a, b, Constant(a_v+b_v))]
    elif mode == 2 :
        a_v = int(a)
        c_v = int(c)
        return [(a, Constant(c_v-a_v), c)]
    else :
        b_v = int(b)
        c_v = int(c)
        return [(Constant(c_v-b_v), b, c)]
    return []

def addStandardBuiltIns(engine, b=None, s=None) :
    """Add Prolog builtins to the given engine."""
    
    # Shortcut some wrappers
    if b == None : b = BooleanBuiltIn
    if s == None : s = SimpleBuiltIn
    
    engine.addBuiltIn('true', 0, b(builtin_true))
    engine.addBuiltIn('fail', 0, b(builtin_fail))
    engine.addBuiltIn('false', 0, b(builtin_fail))

    engine.addBuiltIn('=', 2, s(builtin_eq))
    engine.addBuiltIn('\=', 2, b(builtin_neq))
    engine.addBuiltIn('==', 2, b(builtin_same))
    engine.addBuiltIn('\==', 2, b(builtin_notsame))

    engine.addBuiltIn('is', 2, s(builtin_is))

    engine.addBuiltIn('>', 2, b(builtin_gt))
    engine.addBuiltIn('<', 2, b(builtin_lt))
    engine.addBuiltIn('=<', 2, b(builtin_le))
    engine.addBuiltIn('>=', 2, b(builtin_ge))
    engine.addBuiltIn('=\=', 2, b(builtin_val_neq))
    engine.addBuiltIn('=:=', 2, b(builtin_val_eq))

    engine.addBuiltIn('var', 1, b(builtin_var))
    engine.addBuiltIn('atom', 1, b(builtin_atom))
    engine.addBuiltIn('atomic', 1, b(builtin_atomic))
    engine.addBuiltIn('compound', 1, b(builtin_compound))
    engine.addBuiltIn('float', 1, b(builtin_float))
    engine.addBuiltIn('rational', 1, b(builtin_rational))
    engine.addBuiltIn('integer', 1, b(builtin_integer))
    engine.addBuiltIn('nonvar', 1, b(builtin_nonvar))
    engine.addBuiltIn('number', 1, b(builtin_number))
    engine.addBuiltIn('simple', 1, b(builtin_simple))
    engine.addBuiltIn('callable', 1, b(builtin_callable))
    engine.addBuiltIn('dbreference', 1, b(builtin_dbreference))
    engine.addBuiltIn('primitive', 1, b(builtin_primitive))
    engine.addBuiltIn('ground', 1, b(builtin_ground))
    engine.addBuiltIn('is_list', 1, b(builtin_is_list))
    
    engine.addBuiltIn('=..', 2, s(builtin_split_call))
    engine.addBuiltIn('arg', 3, s(builtin_arg))
    engine.addBuiltIn('functor', 3, s(builtin_functor))
    
    engine.addBuiltIn('@>',2, b(builtin_struct_gt))
    engine.addBuiltIn('@<',2, b(builtin_struct_lt))
    engine.addBuiltIn('@>=',2, b(builtin_struct_ge))
    engine.addBuiltIn('@=<',2, b(builtin_struct_le))
    engine.addBuiltIn('compare',3, s(builtin_compare))

    engine.addBuiltIn('length',2, s(builtin_length))

    engine.addBuiltIn('sort',2, s(builtin_sort))
    engine.addBuiltIn('between', 3, s(builtin_between))
    engine.addBuiltIn('succ',2, s(builtin_succ))
    engine.addBuiltIn('plus',3, s(builtin_plus))
