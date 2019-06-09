import io

from yuuno2.resource_manager import _resources


def to_dot() -> str:
    f = io.StringIO()
    print("digraph Resources {", file=f)
    print("  node [shape=record]", file=f)

    d = dict(_resources)
    for k, v in d.items():
        r = repr(k).replace("<", "\\<").replace(">", "\\>")
        color = "#ff0000" if v.released else "#000000"
        fill = 'fill="#00ffff"' if v.parent_dead else ''
        print(f'  o{id(k)} [label="{r} | {v.acquired}" color="{color}" {fill}]', file=f)

    for k, v in d.items():
        for c in v.children:
            print(f'  o{id(k)} -> o{id(c)}', file=f)

    print("}", file=f)

    return f.getvalue()
