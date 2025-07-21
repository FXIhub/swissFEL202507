import sys,os
import numpy as np
import matplotlib.pyplot as plt
import h5py
import glob

def get_streak_num(run_id):
    streak_dir = f'/sf/bernina/exp/25g_chapman/work/streaks_ahmed/'
    data_dir = f'/sf/bernina/exp/25g_chapman/raw/run{run_id:04d}/data/'

    data_files = glob.glob(data_dir + f'acq*.JF07T32V02.h5')
    data_files.sort()
    num_data_files = len(data_files)

    print(f"num_data_files: {num_data_files}")

    num_frame_total = 0
    for file in data_files:
        with h5py.File(file,'r') as D:
            num_frame_total += D['data/JF07T32V02/data'].shape[0]

    print(f'num_frame_total: {num_frame_total}')
    streak_files = glob.glob(streak_dir + f'streaks_run{run_id:04d}_file*.h5')
    print(f"num_streak_files: {len(streak_files)}")

    num_frames_included = 0

    streak_file_id_lst = []
    streak_frame_id_lst = []
    pulse_id_lst = []
    counts_lst = []
    for f in streak_files:
        file_id = int(os.path.basename(f).split('.')[0].split('file')[1])
        streak_file_id_lst += [file_id]
        with h5py.File(f,'r') as S:
            # print(list(S))
            streak_frame_id = np.array(S['streak_ids']).tolist()
            counts_lst += [np.array(S['counts']).tolist()]
            pulse_id_lst += [np.array(S['pulse_id']).tolist()]

            streak_frame_id_lst += [streak_frame_id]
            # file_name = S['file_name']
            num_frames_included += len(np.unique(streak_frame_id))
            streaks = S['streaks']


    file_frame_id_arry_all = []
    num_streaks = []
    # frame_counts = []

    for m in range(len(streak_file_id_lst)):
        file_id = streak_file_id_lst[m]
        frame_id = streak_frame_id_lst[m]
        frame_id = np.array(frame_id)
        frame_id_unique, indices = np.unique(frame_id,return_index=True)
        print(file_id)
        file_frame_id_arry_all += np.hstack((np.repeat(file_id,\
                                        frame_id_unique.shape[0]).reshape(-1,1),frame_id_unique.reshape(-1,1))).tolist()
        for frame in frame_id_unique:
            ind = (np.array(frame_id)==frame).nonzero()[0]
            num_streaks += [ind.shape[0]]
        # print(frame_id_unique.shape,len(num_streaks))
    file_frame_id_arry_all = np.array(file_frame_id_arry_all)
    num_streaks = np.array(num_streaks)

    file_frame_id_arry_all = np.hstack((np.repeat(run_id,num_streaks.shape[0]).reshape(-1,1),file_frame_id_arry_all.reshape(-1,2),num_streaks.reshape(-1,1)))
    hit_thld = 15
    ind = (num_streaks>=hit_thld)

    #### output the file and frame list file
    # file_frame_id_arry_all = np.array(file_frame_id_arry_all)
    file_frame_id_arry_all = file_frame_id_arry_all[ind]
    output_dir = '/sf/bernina/exp/25g_chapman/work/stas_zhangwe/'
    np.savetxt(output_dir + f'hit_frame_list_run{run_id:04d}.txt',file_frame_id_arry_all,fmt=['%04d','%04d','%5d','%5d'])
    ####
    num_hits_total = ind.sum()
    hit_rate = num_hits_total/num_frame_total*100

    return hit_rate, num_hits_total, num_frame_total, num_data_files,streak_file_id_lst, streak_frame_id_lst,num_streaks,counts_lst,pulse_id_lst

if __name__=='__main__':
    run_id = int(sys.argv[1])
    hit_stats = get_streak_num(run_id)
    print(f"hit rate for run {run_id} is {hit_stats[0]:.2f}, hits_total {hit_stats[1]}, frames_total : {hit_stats[2]}")
    print(f"{hit_stats[3]} data files")
    num_streaks = hit_stats[-3]
    plt.figure()
    plt.hist(num_streaks,bins=np.linspace(0,100,101))
    plt.title(f'number of streaks run {run_id:04d}')
    plt.yscale('linear')
    # plt.ylim(0,300)
    plt.show()


