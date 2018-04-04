import multiprocessing

from tqdm import tqdm, tqdm_notebook


class TasksPoolHandler:
    def __init__(self, n_workers=None, pbar=True, ipython_notbook=False):
        if n_workers is None:
            n_workers = multiprocessing.cpu_count() * 4

        self.pool = multiprocessing.Pool(processes=n_workers)

        if pbar:
            if not ipython_notbook:
                self.pbar = tqdm
            else:
                self.pbar = tqdm_notebook
        else:
            self.pbar = None

    def map(self, task, args):
        results = []
        total = len(args)
        iterator = self.pool.map(task, args)

        if self.pbar is not None:
            iterator = self.pbar(iterator, total=total)

        for result in iterator:
            results.append(result)

        return results

    def close(self):
        self.pool.close()

    def join(self):
        self.pool.join()

    def __del__(self):
        self.close()
        self.join()
