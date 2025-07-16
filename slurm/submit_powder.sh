#!/bin/bash

#SBATCH --reservation=p22263_2025-07-15
#SBATCH --time=1000
#SBATCH --job-name=powder
#SBATCH --output=powder-%A-%a.out
#SBATCH --error=powder-%A-%a.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1 

module load anaconda
conda config --add envs_dirs /das/work/p22/p22263/venvs/
conda activate ra-standard_py39

python powder.py $1

