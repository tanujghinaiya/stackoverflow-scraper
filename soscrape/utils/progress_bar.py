import time

from tqdm import tqdm, tqdm_notebook


class ProgressBar:
    def __init__(self, n, ipython_notebook=False):
        self.n = n
        if ipython_notebook is not False:
            self.pbar = tqdm_notebook(total=n)
        else:
            self.pbar = tqdm(total=n)
        self.i = 0
        self.start_time = time.time()

    def update(self, n=1):
        self.i += n
        if self.i <= self.n:
            self.pbar.update(n)

    def write(self, str):
        self.pbar.write(str)

    def finish(self):
        self.write('Completed %d tasks in %f seconds' % (self.i, time.time() - self.start_time))
        self.pbar.close()
