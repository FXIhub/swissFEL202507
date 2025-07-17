#!/bin/bash


# get number of files in run
echo argument = $1
run=$(printf %04d $1)
echo run = $run
run_dir=/sf/bernina/exp/25g_chapman/raw/run${run}/data
echo run_dir = $run_dir
files=$(ls ${run_dir}/acq*.JF*.h5 | wc -w)
echo found ${files} Jungfrau files in run directory ${run_dir}
echo sbatch --parsable --array=1-${files} submit_streakfinder_single_file.sh $1

# launch jop for each file
ID=$(sbatch --parsable --array=1-${files} submit_streakfinder_single_file.sh $1)

# launch job to merge and cleaup files
ID2=$(sbatch --depend=afterok:${ID} --parsable submit_streakfinder_finish.sh $1)

ID2=$(sbatch --depend=afterok:${ID2} --parsable submit_add_geometry.sh $1)
