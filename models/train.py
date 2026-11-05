"""Entry point; all annotations must pass the mandatory preflight gate."""
from training_pipeline import run, ROOT
if __name__ == '__main__':
    run(ROOT/'models/unet_laptop.json')
