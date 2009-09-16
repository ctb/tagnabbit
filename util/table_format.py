x = """
Aggregation
Behavior
Communication
Complexity
Cooperation
Ecology
Epidemiology
Evolvability
Fitness Landscapes
Gene Networks
Genomics
Historical Contingency
Information Theory
Intelligence
Memory
Metagenomics
Multi-level selection
Navigation
Neural Networks
Phylogeny Reconstruction
Plasticity
Recognition
Robustness
Speciation
"""

y = """
Biological Evolution
Computational Evolution
Applied Evolution
"""

z = """
K-12 Education
Undergraduate Education
Graduate Education
Postdoc Education
Public Outreach
Industrial Outreach
"""

###

print '<table width="100%">'
for target in x, y, z:

    lines = target.strip().splitlines()

    n_cols = 3
    cols = [ list() for n in range(n_cols) ]

    n_rows = len(lines) / n_cols
    for i in range(n_rows):
        for j in range(n_cols):
            try:
                cols[j].append(lines[j * n_rows + i])
            except IndexError:
                continue

    if len(lines) % n_cols:
        i += 1
        for j in range(n_cols):
            try:
                cols[j].append(lines[j * n_rows + i])
            except IndexError:
                continue

    for i in range(n_rows + 1):
        print '<tr>'
        for j in range(n_cols):
            col = cols[j]
            try:
                print '<td><a href="#">%s</a></td>' % (col[i]),
            except IndexError:
                print '<td></td>',
        print '\n</tr>'

    print '<tr><td colspan="%d"><hr></td></tr>' % (n_cols,)
print '</table>'
