# Final binary anemia model

Place the final image-only ONNX classifier here as `model.onnx`.

Expected input: `[1, 3, 224, 224]` float32.

The API uses RGB → resize 224×224 → `/255` → ImageNet normalization → CHW preprocessing.

The classifier is binary. The API returns an anemia probability and applies a 0.50 classification threshold.

This folder is intended to contain the final `model.onnx` supplied for the AnemoScan binary project.
