import torch
from models.yolo import Model
from utils.general import set_logging
from utils.torch_utils import select_device
import yaml

def convert_to_onnx(weight_path, img_size, yaml_config, onnx_path):
    set_logging()
    device = select_device('cpu')  # 选择CPU进行模型转换

    # 加载模型配置和权重
    with open(yaml_config) as f:
        yaml_data = yaml.safe_load(f)
    model = Model(yaml_data, ch=3, nc=yaml_data['nc'], anchors=yaml_data['anchors']).to(device)
    ckpt = torch.load(weight_path, map_location=device)  # 确保权重与设备匹配
    model.load_state_dict(ckpt['model'].state_dict())

    model.eval()
    img = torch.zeros((1, 3, img_size, img_size)).to(device)  # 创建一个虚拟的输入张量

    # 导出到ONNX格式
    torch.onnx.export(model, img, onnx_path, verbose=False, opset_version=12,
                      input_names=['images'], output_names=['output'],
                      dynamic_axes={'images': {0: 'batch_size'}, 'output': {1: 'batch_size'}})

    print(f"模型已转换为ONNX格式并保存到 {onnx_path}")

# 这里需要根据你的实际情况替换下列变量中的路径
weight_path = 'runs/train/exp5/weights/best.pt' # 模型权重文件的路径
img_size = 640  # 训练时使用的图像尺寸
yaml_config = 'C:/Users/11566/Desktop/yolov5-7.0/yolov5-7.0/data/my_data.yaml' # YOLOv5配置文件的路径
onnx_path = 'C:/Users/11566/Desktop/onnx/your_model.onnx' # 保存ONNX模型的路径

# 执行模型转换
convert_to_onnx(weight_path, img_size, yaml_config, onnx_path)
