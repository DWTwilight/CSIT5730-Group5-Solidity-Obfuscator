from flattening import FlatteningContext

ctx = FlatteningContext('./branch-flattening/examples/example1.sol')

output = ctx.flatten()

# write to file
with open('./branch-flattening/examples/example1_flattened.sol', 'w') as f:
    f.write(output)



