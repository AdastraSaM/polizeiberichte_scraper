import pandas as pd
import numpy as np
from modules import transformer_tools as tt
import glob


berichte = pd.concat([pd.read_csv(f, sep=";", header="infer", encoding="UTF-8") for f in glob.glob(r"../out/ffm_news*.csv")])
print(berichte.count())