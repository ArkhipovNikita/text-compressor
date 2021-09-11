import argparse


def get_io_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action='store', dest='input_path', type=str)
    parser.add_argument('-o', action='store', dest='output_path', type=str)

    args = parser.parse_args()

    return args.input_path, args.output_path
