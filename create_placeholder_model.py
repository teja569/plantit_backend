# Create a simple placeholder ONNX model for testing
import numpy as np
import onnx
from onnx import helper, TensorProto

# Create a simple model that outputs random predictions
# This is just for testing - replace with your actual trained model

# Define input shape (batch_size, channels, height, width)
input_shape = [1, 3, 224, 224]

# Create input tensor
input_tensor = helper.make_tensor_value_info(
    'input',
    TensorProto.FLOAT,
    input_shape
)

# Create output tensors
output1 = helper.make_tensor_value_info(
    'is_plant_prob',
    TensorProto.FLOAT,
    [1, 1]
)

output2 = helper.make_tensor_value_info(
    'plant_type_probs',
    TensorProto.FLOAT,
    [1, 15]  # 15 plant types
)

# Create a simple identity node (for testing)
node = helper.make_node(
    'Identity',
    inputs=['input'],
    outputs=['is_plant_prob']
)

# Create the graph
graph = helper.make_graph(
    [node],
    'plant_classifier',
    [input_tensor],
    [output1, output2]
)

# Create the model
model = helper.make_model(graph)

# Save the model
onnx.save(model, 'models/plant_classifier.onnx')

print("Placeholder ONNX model created successfully!")
print("Replace this with your actual trained model for production use.")
