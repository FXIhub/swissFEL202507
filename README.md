# swissFEL202507
Convergent Beam Diffraction cystallography experiment at the Bernina beamline with the Junfrau detector

Beamtime directory: `/sf/bernina/exp/25g_chapman`

## analysis scripts

SSH to ra (see SSH below)

### calculate whitefield
```
$ cd /sf/bernina/exp/25g_chapman/work/git/swissFEL202507/slurm
$ sbatch submit_whitefield.sh <run_number>
```
This outputs:
```
$ h5ls -r /sf/bernina/exp/25g_chapman/work/whitefield/whitefield_run<run_number>.h5 
/                        Group
/std                     Dataset {16448, 1030}
/whitefield              Dataset {16448, 1030}
```
which is required by the streak finder.

### calculate streaks
```
$ cd /sf/bernina/exp/25g_chapman/work/git/swissFEL202507/slurm
$ sbatch submit_streakfinder.sh <run_number>
```
if you wish to change the peak finding parameters edit the file: 
	`/sf/bernina/exp/25g_chapman/work/git/swissFEL202507/slurm/streak_finder_params.json`

this outputs a list of streaks to:
```
$ h5ls -r /sf/bernina/exp/25g_chapman/work/streaks/streaks_run<run_number>.h5
/                        Group
/counts                  Dataset {737404}
/file_index              Dataset {26573}
/file_name               Dataset {737404}
/fs0_ss0_fs1_ss1_im      Dataset {737404, 4}
/pulse_id                Dataset {26573, 1}
/ss0_fs0_ss1_fs1_slab    Dataset {737404, 4}
```

### plot powder
load jupyter notebook from `/sf/bernina/exp/25g_chapman/work/git/swissFEL202507/analysis/plot_powder.ipynb`


## Links
- [SwissFEL Google doc](https://docs.google.com/document/d/1mA43zji2rCJHscgj-RfL8fwlKnjQ1flEnQeekHcOKoM/)
- [XWiki page](https://xwiki.desy.de/xwiki/bin/view/MLL/SwissFEL_July_2025)
- [Mattermost link](https://chat.desy.de/desy/channels/swissfel-202507)
- [SciLog](https://scilog.psi.ch/logbooks/677f5e86ff60c08c7abab0d2/dashboard)

## External SSH access
SSH works for me! Here is my process. 

You can just do **terminal 1** and **terminal 2** steps if you don't care about having non-password ssh connections after establishing the first ssh connection.

### SSH
```bash
$ cat .ssh/config
Host *.psi.ch
        ControlMaster auto
        ControlPath ~/.ssh/controlmasters/%r@%h:%p
        ControlPersist yes
$ mkdir ~/.ssh/controlmasters
```

**terminal 1**: 
 - `$ ssh ext-morgan_a@hopx.psi.ch` 
 - enter password
 - enter mfa
 - leave terminal running

**terminal 2**:
 - `$ ssh -J ext-morgan_a@hopx.psi.ch ext-morgan_a@ra.psi.ch`
 - enter password
 - leave terminal running

you now have access to ra cluster

**terminal 3**:
- `$ ssh ext-morgan_a@ra.psi.ch`

You now have access to ra without entering a password or MFA.

There is probably a way to configure ssh to make this easier.
