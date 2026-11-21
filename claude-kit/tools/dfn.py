import sys, soundfile as sf, torch
from df.enhance import enhance, init_df
m, st, _ = init_df(model_base_dir="/root/tools/models/DeepFilterNet3")
a, sr = sf.read(sys.argv[1], dtype='float32'); assert sr == st.sr()
out = enhance(m, st, torch.from_numpy(a)[None], atten_lim_db=None)
sf.write(sys.argv[2], out[0].numpy(), sr)
