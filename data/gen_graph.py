import os, networkx as nx
import xml.etree.ElementTree as ET

# path to Mathlib folder
graph_path = os.path.join(os.path.dirname(__file__), 'graph.gexf')
root = ET.parse(graph_path).getroot()
output_filename = os.path.join(os.path.dirname(__file__), '../src/visualizer/import_graph.txt')

'''
The steps to generate a graph data file:
1. set up lean4, lake and mathlib
2. run 'lake exe graph' to get the .dot file of import relations
3. run this script to generate a 'import_graph.txt' file,
  which you may use to replace the one under data/ folder.

The algorithm implemented in this script:

For each node:
  assign x according to |{y s.t. x is dependent on y}|
  assign y according to its topic, with some ad-hoc spacing mechanism
  assign radius according to its page-rank weight

There are certainly other interesting ways to visualize these nodes, e.g.
- size a node according to its degree/line-of-code etc.
- make the graph radial.
If you would like to try your own ideas, read the output section, and fill these data by yourself.
'''

# load graph from gexf file
G = nx.DiGraph()
node_rank = {}
for node in root.findall(".//{*}node"):

  node_id = node.attrib.get('id')
  decl_count = float(node.find('.//{*}attvalue').attrib.get('value'))
  node_rank[node_id] = decl_count

for edge in root.findall(".//{*}edge"):
  src = edge.attrib.get('source')
  dst = edge.attrib.get('target')
  G.add_edge(src, dst)

# print #nodes and #edges
print(f'# of nodes: {G.number_of_nodes()}')
print(f'# of edges: {G.number_of_edges()}')

# topological sort
topo_sort_nodes = list(nx.topological_sort(G))
topo_sort = {node: i for i, node in enumerate(topo_sort_nodes)}


# assign positions

dep_closure = [set(nx.ancestors(G, node)) for node in topo_sort_nodes]
horizontal_position = [len(dep_closure[i]) ** 0.72 for i in range(len(dep_closure))]
vertical_position = [0 for i in range(len(dep_closure))]

red = '#ff0000'
orange = '#ff8000'
blue = '#6040ff'
light_blue = '#0080ff'
green = '#00ff00'
yellow = '#ffff00'
dark_yellow = '#bfff00'
purple = '#8000ff'
pink = '#ff00ff'
brown = '#804000'
cyan = '#00ffff'
gray = '#808080'
dark_gray = '#404040'
dark_green = '#008040'
light_red = '#ff8080'
dark_red = '#800000'
light_purple = '#ff80ff'
navy = '#0000ff'

color_and_rest_v = [
  ('Tactic', '#404080', 90),
  ('InformationTheory', purple, 132),
  ('Combinatorics', dark_red, 130),
  ('GroupTheory', '#ff2040', 120),
  ('FieldTheory', '#ffff80', 125),
  ('RingTheory', orange, 115),
  ('RepresentationTheory', red, 107),
  ('Algebra', yellow, 100),
  ('Init', dark_green, 90),
  ('NumberTheory', dark_red, 90),
  ('LinearAlgebra', green, 82),
  ('Order', brown, 85),
  ('Logic', light_blue, 75),
  ('SetTheory', light_red, 80),
  ('Data', dark_gray, 80),
  ('AlgebraicGeometry', blue, 80),
  ('Computability', dark_yellow, 75),
  ('ModelTheory', blue, 110),
  ('Geometry', light_purple, 70),
  ('CategoryTheory', '#80a0ff', 62),
  ('Analysis', cyan, 57),
  ('AlgebraicTopology', blue, 48),
  ('Condensed', red, 48),
  ('Topology', pink, 40),
  ('MeasureTheory', purple, 30),
  ('Dynamics', dark_green, 25),
  ('Probability', navy, 20),
  ('Lean', '#202020', 80),
]

def get_group(node):
  for prefix, color, y in color_and_rest_v:
    paths = node.split(".")
    if len(paths) > 1 and paths[0] == "Mathlib" and paths[1] == prefix:
      return prefix, color, y
  return ('', '#202020', 140)

def get_predecessors_in_same_group(node):
  prefix, color, y = get_group(node)
  return [n for n in G.predecessors(node) if get_group(n)[0] == prefix]

buckets = {i: set() for i in range(-10, 1000)}

horizontal_zero_spread_out = 0

for i in range(len(topo_sort_nodes)):
  node = topo_sort_nodes[i]
  prefix, color, y = get_group(node)
  vertical_position[i] = y

  if horizontal_position[i] == 0:
    horizontal_position[i] = -horizontal_zero_spread_out
    horizontal_zero_spread_out += 1
    horizontal_zero_spread_out %= 10


  buckets[int(horizontal_position[i])].add(i)



def get_next_slot(i):
  d = i // 2
  sign = 1 if i % 2 == 0 else -1
  return sign * d


for i, bucket in buckets.items():
  vertical_bucket = [False for _ in range(300)]
  for node in bucket:
    sum_y = vertical_position[node]
    for pred in get_predecessors_in_same_group(topo_sort_nodes[node]):
      sum_y += vertical_position[topo_sort[pred]]
    avg_y = sum_y / (len(get_predecessors_in_same_group(topo_sort_nodes[node])) + 1)

    slot = 0
    while vertical_bucket[int(avg_y + get_next_slot(slot))]:
      slot += 1

    vertical_position[node] = avg_y + get_next_slot(slot)
    vertical_bucket[int(vertical_position[node])] = True

max_rank = max(node_rank.values())
min_rank = min(node_rank.values())
print('max:', max_rank, 'min:', min_rank)

with open(output_filename, 'w') as f:
  # first line
  f.write(f'{G.number_of_nodes()}\n')

  for node, index in topo_sort.items():
    prefix, color, y = get_group(node)
    rank = node_rank[node]
    radius = 0.2 + 3 * ((rank - min_rank) / (max_rank - min_rank))

    # one node per line: position, color and size
    f.write(f'{node} {color} {horizontal_position[index]} {vertical_position[index]} {radius}\n')

  for node, index in topo_sort.items():
    successors = list(G.neighbors(node))

    # one node per line
    f.write(f'{index} {len(successors)} ' + ' '.join([str(topo_sort[n]) for n in successors]) + '\n')
