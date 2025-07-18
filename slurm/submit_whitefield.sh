#!/bin/bash

#SBATCH --reservation=p22263_2025-07-15
#SBATCH --time=60
#SBATCH --mem=0
#SBATCH --job-name=whitefield
#SBATCH --output=whitefield-%A-%a.out
#SBATCH --error=whitefield-%A-%a.out

module load anaconda
conda config --add envs_dirs /das/work/p22/p22263/venvs/
# conda activate dap-sf-new
conda activate cbc_v2

python whitefield.py $1
