"""phygeonet eval"""
import numpy as np
import mindspore as ms
from sklearn.metrics import mean_squared_error as cal_mse

from sciai.context import init_project
from sciai.utils import print_log, data_type_dict_amp
from sciai.utils.python_utils import print_time
from src.network import Net, USCNN
from src.plot import plot_train_process
from src.process import get_data, prepare
from src.py_mesh import to4_d_tensor


def evaluate(net, args, dataset, ofv_sb):
    """evaluate"""
    m_res = 0
    e_v = 0
    batch_num = len(dataset)
    cnnv_numpy, coord, output_v = None, None, None
    training_data_loader = dataset.create_dict_iterator()
    for batch in training_data_loader:
        _, coord, _, _, _, jinv, dxdxi, dydxi, dxdeta, dydeta = to4_d_tensor(batch.values())
        loss, output_v = net(coord, jinv, dxdxi, dydxi, dxdeta, dydeta)
        m_res += loss
        cnnv_numpy = output_v[0, 0, :, :]
        e_v += np.sqrt(cal_mse(ofv_sb, cnnv_numpy) / cal_mse(ofv_sb, ofv_sb * 0))
    print_log(f"m_res Loss:{m_res / batch_num}, e_v Loss:{e_v / batch_num}")
    if args.save_fig:
        epoch = "val"
        plot_train_process(args, coord, epoch, ofv_sb, output_v)
    return m_res / batch_num, e_v / batch_num


@print_time("eval")
def main(args):
    dtype = data_type_dict_amp.get(args.amp_level, ms.float32)
    dataset, h, nvar_input, nvar_output, nx, ny, ofv_sb = get_data(args)
    model = USCNN(h, nx, ny, nvar_input, nvar_output)
    net = Net(model, args.batch_size, h)
    net.to_float(dtype)
    ms.load_checkpoint(args.load_ckpt_path, net)
    evaluate(net, args, dataset, ofv_sb)


if __name__ == "__main__":
    args_ = prepare()
    init_project(args=args_[0])
    main(*args_)
