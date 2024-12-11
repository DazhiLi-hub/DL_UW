from collections import defaultdict

def read_and_convert_to_dsl(input_filename, output_filename):
    # Open the input file and read the lines
    with open(input_filename, 'r') as infile:
        edges = infile.readlines()

    result = defaultdict(set)

    for edge in edges:
        # Strip any extra spaces or newline characters and split the line into two integers
        node1, node2 = edge.strip().split()
        result[int(node1)].add(int(node2))
        result[int(node2)].add(int(node1))

    sorted_dict = {key: result[key] for key in sorted(result)}

    # Open the output DSL file for writing
    with open(output_filename, 'w') as outfile:
        # Write the edge in the desired DSL format
        for k,v in sorted_dict.items():
            outfile.write(f"{k}=")  # Example format: "node1 -> node2"
            vertices = list(v)
            vertices.sort()
            num_vertices = len(vertices)
            for i in range(num_vertices - 1):
                outfile.write(f"{vertices[i]},1;")
            outfile.write(f"{vertices[-1]},1\n")



# Example usage
input_filename = "graph100.txt"  # Your input file with edges
output_filename = "graph100.dsl"  # Output DSL file

read_and_convert_to_dsl(input_filename, output_filename)