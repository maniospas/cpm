import sys
import pathlib
import re

associations: dict[str,str] = dict()

def eq(source: str, i: int, needle: str):
    return source[i:min(len(source), i+len(needle))]==needle

def find_next(source: str, i: int, needle: str, end=None):
    if end is None: end=len(source)
    while not eq(source, i, needle) and i<end:
        i += 1
    if i<len(source): return i
    return None

def safeget(source: str, i: int):
    if i<0 or i>=len(source): return ""
    return source[i]

def find_next_kw(source: str, i: int, needle: str, end=None):
    if end is None: end=len(source)
    while not (eq(source, i, needle) and safeget(source, i-1) in " \n\t\r[](){}=<>.+-/*%&|;,!" and safeget(source, i+len(needle)) in " \n\t\r[](){}=<>.+-/*%&|;,!") and i<end:
        i += 1
    if i<len(source): return i
    return None

def transpile_struct(source: str, i: int):
    helpers_before = ""
    helpers = ""
    ret = "typedef struct "
    start = find_next(source, i+6, "{")
    struct_name = source[i+6:start].strip(" \n\t\r")
    assert struct_name, "empty class name"
    ret += struct_name+"{"
    end = start
    depth = 0
    while end<len(source):
        if source[end]=="{": depth+=1
        if source[end]=="}": depth-=1
        if not depth: break
        end += 1
    assert not depth, "class definition never closed"

    i = start+1
    while i<end:
        prev_i = i
        i = find_next_kw(source, i, "pub")
        if i is None:
            ret += source[prev_i:end]
            break
        ret += source[prev_i:i]
        i += len("pub")
        signature_start = find_next(source, i, "(", end)
        pub_name = source[i:signature_start].strip().split(" ")[-1]
        has_ret_type = pub_name!=source[i:signature_start].strip()
        assert pub_name not in associations, "already defined "+pub_name+" for class "+struct_name
        #print(struct_name+"."+pub_name)
        associations[pub_name] = struct_name
        signature = source[i:signature_start].strip()+"(struct "+struct_name+" *this,"
        if not has_ret_type: signature = "struct "+struct_name+"* "+signature
        signature_end = find_next(source, i, "{", end)
        signature += source[signature_start+1:signature_end]
        signature = signature.replace(",)", ")").rstrip() # TODO: not proper accounting for no arguments
        body_end = signature_end
        depth = 0
        while body_end<end:
            if source[body_end]=="{": depth+=1
            if source[body_end]=="}": depth-=1
            if not depth: break
            body_end += 1
        assert not depth, "pub definition never ended "+source[signature_end:body_end]
        helpers_before += signature+";\n"
        helpers += signature+source[signature_end:body_end].rstrip()
        if not has_ret_type: helpers += "return this;"
        helpers += "}\n"
        i = body_end + 1

    i = find_next(source, end, ";")
    ret += source[end:i]+" "+struct_name+";\n"
    if helpers_before: helpers_before = "struct "+struct_name+";\n"+helpers_before
    return i+1, helpers_before+ret+helpers.replace("self", "(*this)")


def transpile(source: str):
    # canonical form with less spaces and line breaks (we DO need `()` to not have spaces inside)
    prev_len = 0
    while len(source)!=prev_len:
        source = source.replace(" )", ")").replace("( ", ")").replace(", ", ",").replace(" ,", ",").replace(". ", ".").replace("\n\n", "\n")
        prev_len = len(source)
    # parse class definitions
    ret = ""
    i = 0
    while i<len(source):
        prev_i = i
        i = find_next_kw(source, i, "class")
        if i is None:
            ret += source[prev_i:]
            break
        ret += source[prev_i:i]
        i, temp = transpile_struct(source, i)
        ret += temp
    return ret

def replace_call(source: str):
    ret = ""
    i = 0
    while i<len(source):
        if source[i]=="." or (i<len(source)-1 and source[i]=="-" and source[i+1]==">"):
            prev_i = i
            take_referefence = source[i]=="."
            i += 1 if source[i]=="." else 2
            pub_name_end = find_next(source, i, "(")
            pub_name = source[i:pub_name_end].strip()
            if pub_name in associations:
                i = pub_name_end+1
                expression_start = len(ret)
                depth = 0
                while True:
                    expression_start -= 1
                    assert expression_start>0, "failed to obtain expression just before pub method call"
                    if ret[expression_start] in ")}]": depth += 1
                    if ret[expression_start] in "({[": depth -= 1
                    if depth==0 and ret[expression_start] in "=<>.+-/*%&|;,!)}]": break
                    if depth<0: break
                expression_start += 1
                argument = ret[expression_start:].strip()
                ret = ret[:expression_start]
                if argument.startswith(associations[pub_name]+" "):
                    argument = argument[len(associations[pub_name])+1:]
                    ret += associations[pub_name]+" "+argument+";"
                elif argument.startswith(associations[pub_name]+"*"):
                    argument = argument[len(associations[pub_name])+1:]
                    ret += associations[pub_name]+" "+argument+";"
                if take_referefence: argument = "&("+argument+")"
                ret += pub_name+"("+argument+","
                continue
            i = prev_i
        ret += source[i]
        i += 1
    return ret.replace(",)",")")

def safety(source: str):
    ret = (
        "#include<stdint.h>\n"
        +"typedef int8_t  i8;\n"
        +"typedef int16_t i16;\n"
        +"typedef int32_t i32;\n"
        +"typedef int64_t i64;\n"
        +"typedef uint8_t  u8;\n"
        +"typedef uint16_t u16;\n"
        +"typedef uint32_t u32;\n"
        +"typedef uint64_t u64;\n"
        +"typedef float f32;\n"
        +"typedef double f64;\n"
        +"typedef const char* cstr;\n"
        +"#define delete(ptr) if(ptr)free(ptr);ptr=0;\n"
        +"#define defaults(expr) if(!this) return expr;"
        +source.replace("cstr", "const char*")
    )
    return ret

if __name__ == '__main__':
    if len(sys.argv) != 2: print("Usage: python cpm.py <file.cpm>"); sys.exit(1)
    infile = pathlib.Path(sys.argv[1])
    if not infile.suffix == '.cpm': print("Error: input file must have .cpm extension"); sys.exit(1)
    src = infile.read_text(encoding='utf-8')
    # remove comments
    _comment_re = re.compile(
        r'''
        //.*?$                         |   # // single‑line comment
        /\*.*?\*/                      |   # /* … */ multi‑line comment
        "                              # opening quote of a string
            (?:\\.|[^"\\])*            #   any escaped char or non‑quote
        "                              # closing quote
        ''',
        re.DOTALL | re.MULTILINE | re.VERBOSE
    )
    def _replacer(m: re.Match) -> str:
        return m.group(0) if m.group(0).startswith('"') else '' # If the match starts with a quote we keep it (it’s a string literal).
    src = _comment_re.sub(_replacer, src)
    # take strings away
    _str_table: list[str] = []
    _str_pat = re.compile(r'"(?:\\.|[^"\\])*"')
    def repl(m: re.Match) -> str:
        _str_table.append(m.group(0))
        return f"\"{len(_str_table)-1}\""
    src = _str_pat.sub(repl, src)
    # actually transpile
    out = transpile(src)
    out = replace_call(out)
    out = safety(out)
    # this is optional but a nice feature to have by merging string defs across multiple places
    table_preamble = ""
    found_strings: dict[str, str] = dict()
    for i, raw_string in enumerate(_str_table):
        found_string = found_strings.get(raw_string, None)
        if found_string is not None:
            _str_table[i] = found_string
            continue
        found_string = "____cpm"+str(len(found_strings))
        found_strings[raw_string] = found_string
        _str_table[i] = found_string
        table_preamble += "const char* "+found_string+"="+raw_string+";\n"
    # re-inject strings
    def repl(m: re.Match) -> str:
        idx = int(m.group(1))
        return _str_table[idx]
    out = table_preamble+re.sub(r'"(\d+)"', repl, out)

    infile.with_suffix('.c').write_text(out, encoding='utf-8')
    print(f"{infile.name} converted to {infile.with_suffix('.c').name}")
