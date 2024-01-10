import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--config_parameter", type=str)
args = parser.parse_args()

print(f"Hello {args.config_parameter}!")