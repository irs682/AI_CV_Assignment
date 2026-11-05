"""Held-out evaluation, available only after human verification and training."""
import argparse
from training_pipeline import run, ROOT
if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('checkpoint')
    args=parser.parse_args(); run(ROOT/'models/unet_laptop.json', evaluate=args.checkpoint)
