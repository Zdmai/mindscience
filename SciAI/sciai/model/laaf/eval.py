"""laaf eval"""
import mindspore as ms
from mindspore import ops

from sciai.architecture.basic_block import MLPAAF
from sciai.context import init_project
from sciai.utils import data_type_dict_amp, print_log
from sciai.utils.python_utils import print_time
from src.plot import plot_eval
from src.process import get_data, prepare


@print_time("eval")
def main(args):
    dtype = data_type_dict_amp.get(args.amp_level, ms.float32)
    x, y = get_data(args.num_grid, dtype)
    net = MLPAAF(args.layers, activation=ops.tanh, a_value=0.1, scale=10, share_type="layer_wise")
    if dtype == ms.float16:
        net.to_float(ms.float16)
    ms.load_checkpoint(args.load_ckpt_path, net)
    sol = net(x)
    mse = ops.mean(ops.square(sol - y))
    print_log(f"MSE: {mse.asnumpy()}")
    if args.save_fig:
        plot_eval(args.figures_path, sol, x, y)


if __name__ == "__main__":
    args_ = prepare()
    init_project(args=args_[0])
    main(*args_)
