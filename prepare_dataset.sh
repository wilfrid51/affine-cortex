git pull

python3 sft_dataset.py SCI
python3 sft_dataset.py CDE
python3 sft_dataset.py LGC
python3 sft_dataset.py MTH
python3 sft_dataset.py agentgym:alfworld
python3 sft_dataset.py agentgym:sciworld
python3 sft_dataset.py agentgym:textcraft
python3 sft_dataset.py agentgym:webshop
python3 sft_dataset.py affine:abd-v2
python3 sft_dataset.py affine:ded-v2

git add .
git commit -m "add: dataset"
git push

sleep 1200