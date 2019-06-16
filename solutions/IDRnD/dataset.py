import os
from torch.utils.data import Dataset
import librosa
import torch
import numpy as np
import glob


class Base_Dataset(Dataset):
    def __init__(self, X, y, transforms=None):
        super().__init__()
        self.X = X
        self.y = y
        self.transforms = transforms
        self.sr = 16000

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        audio = self.get_audio(idx)
        if self.transforms:
            audio = self.transforms(audio)

        label = self.get_label(idx)

        return audio, label

    def get_audio(self, idx):
        audio, _ = librosa.core.load(self.X[idx], sr=self.sr)
        return audio

    def get_label(self, idx):
        label = self.y[idx]
        label = torch.Tensor([label]).float()
        return label


class Test_Dataset(Base_Dataset):
    def __init__(self, X, transforms=None):
        super().__init__(X, None, transforms=transforms)

    def get_label(self, idx):
        return self.X[idx]


class MelDataset(Base_Dataset):
    def __init__(self, X, y, folder, transforms=None):
        super().__init__(X, y, transforms=transforms)
        self.folder = folder
        self.pathes = [dict() for _ in range(len(X))]
        self.load()

    def load(self):
        data = os.listdir(self.folder)
        for name in data:
            if name == ".ipynb_checkpoints": continue
            idx = int(name.split("_")[1].split(".")[0])
            if name not in self.pathes[idx]:
                self.pathes[idx][name] = 0

    def get_audio(self, idx):
        if idx % 10000 == 0:
            self.load()
        min_ = min(self.pathes[idx].keys(), key=lambda x: self.pathes[idx][x])
        path = os.path.join(self.folder, min_)
        self.pathes[idx][min_] += 1
        mel = np.load(path, allow_pickle=True)
        return mel


def get_train_data():
    dataset_dir = "/src/workspace/data/files/"
    train_dataset_dir = os.path.join(dataset_dir, "Training_Data/")

    X = sorted(glob.glob(os.path.join(train_dataset_dir, '**/*.wav'), recursive=True))
    y = np.array([1 if "human" in i else 0 for i in X])
    X = np.array(X)
    return X, y