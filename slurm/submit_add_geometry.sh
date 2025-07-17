#!/bin/bash

#SBATCH --reservation=p22263_2025-07-15
#SBATCH --time=120
#SBATCH --mem=0
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name=streakfinder
#SBATCH --open-mode=append
#SBATCH --output=streakfinder.out
#SBATCH --error=streakfinder.out

module load anaconda
conda config --add envs_dirs /das/work/p22/p22263/venvs/
# conda activate dap-sf-new
conda activate cbc_v2

python add_geometry_streaks.py $1

