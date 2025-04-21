import os
import random
from pathlib import Path

random.seed(42)

DATA_PREFIX = Path('../data/')
# Paths to input directories
clean_dir = DATA_PREFIX / Path('ivrit_audio')
noisy_dir = DATA_PREFIX / Path('ivrit_transformed')

# Assumes filenames are the same across clean and noisy
all_files = sorted([f.name for f in noisy_dir.glob('*.wav')])
random.shuffle(all_files)

# Split proportions
n_total = len(all_files)
n_train = int(0.7 * n_total)
n_val = int(0.15 * n_total)
n_test = n_total - n_train - n_val


# Half of each split will be from clean, half from noisy
def split_pairs(files, clean_portion):
    n = len(files)
    half_clean = clean_portion
    half_noisy = n - half_clean
    return files[:half_clean], files[half_clean:n]


# Perform splits
train_files = all_files[:n_train]
val_files = all_files[n_train:n_train + n_val]
test_files = all_files[n_train + n_val:]

train_clean, train_noisy = split_pairs(train_files, len(train_files) // 2)
val_clean, val_noisy = split_pairs(val_files, len(val_files) // 2)
test_clean, test_noisy = split_pairs(test_files, len(test_files) // 2)


# File output helper
def write_paths(file_list, domain, split_name):
    with open(DATA_PREFIX / Path(f'{domain}_{split_name}.list'), 'w') as f:
        for filename in file_list:
            if domain == 'clean':
                f.write(str((clean_dir / Path(filename)).resolve()) + '\n')
            else:
                f.write(str((noisy_dir / Path(filename)).resolve()) + '\n')


# Write all six files
write_paths(train_clean, 'clean', 'train_no_dev')
write_paths(val_clean, 'clean', 'dev')
write_paths(test_clean, 'clean', 'eval')

write_paths(train_noisy, 'noisy', 'train_no_dev')
write_paths(val_noisy, 'noisy', 'dev')
write_paths(test_noisy, 'noisy', 'eval')
