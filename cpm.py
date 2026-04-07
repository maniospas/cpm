import sys
import pathlib

def eq(source: str, i: int, needle: str):
    return source[i:min(len(source), i+len(needle))]==needle

def find_next(source: str, i: int, needle: str, end=None):
    if end is None: end=len(source)
    while not eq(source, i, needle) and i<end:
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
        i = find_next(source, i, "pub")
        if i is None:
            ret += source[prev_i:end]
            break
        ret += source[prev_i:i]
        i += len("pub")
        signature_start = find_next(source, i, "(", end)
        signature = source[i:signature_start].strip()+"(struct "+struct_name+" *this, "
        signature_end = find_next(source, i, "{", end)
        signature += source[signature_start+1:signature_end]
        signature = signature.replace(", )", ")").rstrip() # TODO: not proper accounting for no arguments
        body_end = signature_end
        depth = 0
        while body_end<end:
            if source[body_end]=="{": depth+=1
            if source[body_end]=="}": depth-=1
            if not depth: break
            body_end += 1
        assert not depth, "pub definition never ended "+source[signature_end:body_end]
        helpers_before += signature+";\n"
        helpers += signature+source[signature_end:body_end].rstrip()+"}\n"
        i = body_end + 1

    i = find_next(source, end, ";")
    ret += source[end:i]+struct_name+";\n"
    if helpers_before: helpers_before = "struct "+struct_name+";\n"+helpers_before
    return i+1, helpers_before+ret+helpers.replace("self.", "this->")


def transpile(source: str):
    ret = ""
    i = 0
    while i<len(source):
        prev_i = i
        i = find_next(source, i, "class")
        if i is None:
            ret += source[prev_i:]
            break
        ret += source[prev_i:i]
        i, temp = transpile_struct(source, i)
        ret += temp
    return ret


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python cpm2c.py <file.cpm>")
        sys.exit(1)
    infile = pathlib.Path(sys.argv[1])
    if not infile.suffix == '.cpm':
        print("Error: input file must have .cpm extension")
        sys.exit(1)
    src = infile.read_text(encoding='utf-8')
    out = transpile(src)
    outfile = infile.with_suffix('.c')
    outfile.write_text(out, encoding='utf-8')
    print(f"{infile.name} >> {outfile.name}")
